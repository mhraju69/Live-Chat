
        const room_id = "{{ room_id }}";
        const ws = new WebSocket("ws://" + location.host + "/ws/video/" + room_id + "/");
        //const ws = new WebSocket("wss://ape-in-eft.ngrok-free.app/ws/room/" + room_id + "/");

        let pc;
        let localStream;
        let isMuted = false;
        let isVideoOff = false;
        let callActive = false;

        // DOM Elements
        const startCallBtn = document.getElementById('startCallBtn');
        const muteBtn = document.getElementById('muteBtn');
        const videoBtn = document.getElementById('videoBtn');
        const endCallBtn = document.getElementById('endCallBtn');
        const callStatus = document.getElementById('callStatus');
        const connectionStatus = document.getElementById('connectionStatus');
        const notification = document.getElementById('notification');
        const notificationText = document.getElementById('notificationText');

        // Show notification
        function showNotification(message) {
            notificationText.textContent = message;
            notification.classList.add('show');
            setTimeout(() => {
                notification.classList.remove('show');
            }, 3000);
        }

        // Toggle audio
        function toggleAudio() {
            if (!localStream) return;
            
            const audioTracks = localStream.getAudioTracks();
            if (audioTracks.length > 0) {
                audioTracks[0].enabled = !audioTracks[0].enabled;
                isMuted = !audioTracks[0].enabled;
                
                muteBtn.innerHTML = isMuted ? 
                    '<i class="fas fa-microphone-slash"></i> Unmute' : 
                    '<i class="fas fa-microphone"></i> Mute';
                
                showNotification(isMuted ? 'Microphone muted' : 'Microphone unmuted');
            }
        }

        // Toggle video
        function toggleVideo() {
            if (!localStream) return;
            
            const videoTracks = localStream.getVideoTracks();
            if (videoTracks.length > 0) {
                videoTracks[0].enabled = !videoTracks[0].enabled;
                isVideoOff = !videoTracks[0].enabled;
                
                videoBtn.innerHTML = isVideoOff ? 
                    '<i class="fas fa-video"></i> Video On' : 
                    '<i class="fas fa-video-slash"></i> Video Off';
                
                showNotification(isVideoOff ? 'Video turned off' : 'Video turned on');
            }
        }

        // End call
        function endCall() {
            if (pc) {
                pc.close();
                pc = null;
            }
            
            if (localStream) {
                localStream.getTracks().forEach(track => track.stop());
                localStream = null;
            }
            
            callActive = false;
            callStatus.textContent = 'Call Ended';
            connectionStatus.textContent = 'Disconnected';
            
            startCallBtn.disabled = false;
            startCallBtn.innerHTML = '<i class="fas fa-video"></i> Start Call';
            
            document.getElementById('remoteVideo').srcObject = null;
            
            showNotification('Call ended');
        }

        // Initialize WebRTC
        async function init() {
            try {
                // Get local camera + mic
                localStream = await navigator.mediaDevices.getUserMedia({ 
                    video: true, 
                    audio: true 
                });
                
                document.getElementById('localVideo').srcObject = localStream;
                connectionStatus.textContent = 'Connected';
                showNotification('Camera and microphone ready');
                
            } catch (err) {
                console.error("Camera/Mic error:", err);
                showNotification('Camera or microphone permission denied!');
                connectionStatus.textContent = 'Error';
                return;
            }

            // Create peer connection
            pc = new RTCPeerConnection({
                iceServers: [
                    { urls: 'stun:stun.l.google.com:19302' }
                ]
            });

            // Add local tracks to peer connection
            localStream.getTracks().forEach(track => {
                pc.addTrack(track, localStream);
            });

            // Handle remote stream
            pc.ontrack = (event) => {
                const remoteVideo = document.getElementById('remoteVideo');
                if (!remoteVideo.srcObject) {
                    remoteVideo.srcObject = event.streams[0];
                    showNotification('Remote participant joined');
                }
            };

            // Handle ICE candidates
            pc.onicecandidate = (event) => {
                if (event.candidate) {
                    ws.send(JSON.stringify({
                        action: "candidate", 
                        payload: event.candidate
                    }));
                }
            };

            // Handle connection state changes
            pc.onconnectionstatechange = () => {
                connectionStatus.textContent = pc.connectionState;
                
                if (pc.connectionState === 'connected') {
                    callStatus.textContent = 'In Call';
                    showNotification('Call connected successfully');
                } else if (pc.connectionState === 'disconnected' || pc.connectionState === 'failed') {
                    callStatus.textContent = 'Connection Lost';
                    showNotification('Connection lost');
                }
            };
        }

        // WebSocket message handler
        ws.onmessage = async (event) => {
            const msg = JSON.parse(event.data);
            const action = msg.action;
            const payload = msg.payload;

            if (!pc) return;

            if (action === "offer") {
                await pc.setRemoteDescription(payload);
                const answer = await pc.createAnswer();
                await pc.setLocalDescription(answer);
                ws.send(JSON.stringify({
                    action: "answer", 
                    payload: pc.localDescription
                }));
                callActive = true;
                callStatus.textContent = 'In Call';
                
            } else if (action === "answer") {
                await pc.setRemoteDescription(payload);
                callActive = true;
                callStatus.textContent = 'In Call';
                
            } else if (action === "candidate") {
                await pc.addIceCandidate(payload);
                
            } else if (action === "peer-joined") {
                showNotification('New participant joined the room');
                
            } else if (action === "peer-left") {
                showNotification('Participant left the room');
                document.getElementById('remoteVideo').srcObject = null;
                callStatus.textContent = 'Waiting';
            }
        };

        // Start call button
        startCallBtn.onclick = async () => {
            if (!pc) {
                showNotification('Connection not ready!');
                return;
            }
            
            const offer = await pc.createOffer();
            await pc.setLocalDescription(offer);
            ws.send(JSON.stringify({
                action: "offer", 
                payload: pc.localDescription
            }));
            
            callActive = true;
            callStatus.textContent = 'Calling...';
            startCallBtn.disabled = true;
            startCallBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Calling...';
            
            showNotification('Call initiated');
        };

        // Control button event listeners
        muteBtn.addEventListener('click', toggleAudio);
        videoBtn.addEventListener('click', toggleVideo);
        endCallBtn.addEventListener('click', endCall);

        // Initialize on page load
        init();

        // Handle page unload
        window.addEventListener('beforeunload', () => {
            if (pc) {
                pc.close();
            }
            if (localStream) {
                localStream.getTracks().forEach(track => track.stop());
            }
        });
