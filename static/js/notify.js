// class ModernNotifier {
//     constructor(options = {}) {
//         // Default options
//         this.defaults = {
//             position: 'top-right', // top-right, top-left, bottom-right, bottom-left
//             animation: 'slide', // slide, fade, scale
//             duration: 5000, // auto-close duration in ms
//             maxNotifications: 5, // maximum notifications to show at once
//             soundEnabled: true, // enable notification sound
//             soundPath: '/static/sounds/notify.wav', // path to sound file
//             showCloseButton: true, // show close button
//             showAvatar: true, // show sender avatar
//             avatarPath: '/static/images/default-avatar.png' // default avatar path
//         };

//         // Merge options
//         this.settings = {...this.defaults, ...options};
        
//         // Initialize state
//         this.notificationSound = null;
//         this.soundInitialized = false;
//         this.notificationCount = 0;
//         this.isWindowFocused = true;
//         this.activeTimeouts = new Map();
//         this.container = null;
        
//         // Initialize when DOM is ready
//         if (document.readyState === 'complete' || document.readyState === 'interactive') {
//             this.initialize();
//         } else {
//             document.addEventListener('DOMContentLoaded', () => this.initialize());
//         }
//     }
    
//     initialize() {
//         this.createContainer();
//         if (this.settings.soundEnabled) {
//             this.initSoundSystem();
//         }
//         this.initWebSocket();
        
//         // Track window focus state
//         window.addEventListener('focus', () => this.isWindowFocused = true);
//         window.addEventListener('blur', () => this.isWindowFocused = false);
        
//         // Request notification permission
//         if ("Notification" in window && Notification.permission !== "granted") {
//             Notification.requestPermission();
//         }
//     }
    
//     createContainer() {
//         // Remove existing container if any
//         const existingContainer = document.getElementById('modern-notifier-container');
//         if (existingContainer) {
//             existingContainer.remove();
//         }
        
//         // Create new container
//         this.container = document.createElement('div');
//         this.container.id = 'modern-notifier-container';
//         this.container.className = `modern-notifier ${this.settings.position}`;
        
//         // Apply styles
//         this.applyStyles();
        
//         document.body.appendChild(this.container);
//     }
    
//     applyStyles() {
//         const style = document.createElement('style');
//         style.textContent = `
//             .modern-notifier {
//                 position: fixed;
//                 z-index: 9999;
//                 display: flex;
//                 flex-direction: column;
//                 gap: 12px;
//                 max-width: 320px;
//                 pointer-events: none;
//             }
            
//             .modern-notifier.top-right {
//                 top: 20px;
//                 right: 20px;
//                 align-items: flex-end;
//             }
            
//             .modern-notifier.top-left {
//                 top: 20px;
//                 left: 20px;
//                 align-items: flex-start;
//             }
            
//             .modern-notifier.bottom-right {
//                 bottom: 20px;
//                 right: 20px;
//                 align-items: flex-end;
//             }
            
//             .modern-notifier.bottom-left {
//                 bottom: 20px;
//                 left: 20px;
//                 align-items: flex-start;
//             }
            
//             .modern-notification {
//                 position: relative;
//                 background: #ffffff;
//                 border-radius: 8px;
//                 box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
//                 padding: 16px;
//                 width: 300px;
//                 pointer-events: auto;
//                 transform-origin: center;
//                 display: flex;
//                 gap: 12px;
//                 border-left: 4px solid #4CAF50;
//                 cursor: pointer;
//             }
            
//             .modern-notification:hover {
//                 box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
//             }
            
//             .notification-avatar {
//                 width: 40px;
//                 height: 40px;
//                 border-radius: 50%;
//                 object-fit: cover;
//                 flex-shrink: 0;
//             }
            
//             .notification-content {
//                 flex-grow: 1;
//             }
            
//             .notification-title {
//                 font-weight: 600;
//                 margin-bottom: 4px;
//                 color: #333;
//                 font-size: 14px;
//             }
            
//             .notification-message {
//                 color: #666;
//                 font-size: 13px;
//                 margin-bottom: 8px;
//                 line-height: 1.4;
//             }
            
//             .notification-actions {
//                 display: flex;
//                 justify-content: space-between;
//                 align-items: center;
//                 margin-top: 8px;
//             }
            
//             .notification-link {
//                 color: #4CAF50;
//                 text-decoration: none;
//                 font-size: 12px;
//                 font-weight: 500;
//             }
            
//             .notification-link:hover {
//                 text-decoration: underline;
//             }
            
//             .notification-close {
//                 background: none;
//                 border: none;
//                 color: #999;
//                 cursor: pointer;
//                 font-size: 16px;
//                 line-height: 1;
//                 padding: 0;
//                 position: absolute;
//                 top: 8px;
//                 right: 8px;
//             }
            
//             .notification-close:hover {
//                 color: #555;
//             }
            
//             .notification-progress {
//                 position: absolute;
//                 bottom: 0;
//                 left: 0;
//                 height: 3px;
//                 background: rgba(0, 0, 0, 0.1);
//                 width: 100%;
//                 border-radius: 0 0 8px 8px;
//                 overflow: hidden;
//             }
            
//             .notification-progress-bar {
//                 height: 100%;
//                 background: #4CAF50;
//                 width: 100%;
//                 transform-origin: left;
//                 animation: progressBar ${this.settings.duration}ms linear forwards;
//             }
            
//             @keyframes progressBar {
//                 from { transform: scaleX(1); }
//                 to { transform: scaleX(0); }
//             }
            
//             /* Animation classes */
//             .slide-in {
//                 animation: slideIn 0.3s forwards;
//             }
            
//             .fade-in {
//                 animation: fadeIn 0.3s forwards;
//             }
            
//             .scale-in {
//                 animation: scaleIn 0.3s forwards;
//             }
            
//             .fade-out {
//                 animation: fadeOut 0.3s forwards;
//             }
            
//             @keyframes slideIn {
//                 from { transform: translateX(100%); opacity: 0; }
//                 to { transform: translateX(0); opacity: 1; }
//             }
            
//             @keyframes fadeIn {
//                 from { opacity: 0; }
//                 to { opacity: 1; }
//             }
            
//             @keyframes scaleIn {
//                 from { transform: scale(0.8); opacity: 0; }
//                 to { transform: scale(1); opacity: 1; }
//             }
            
//             @keyframes fadeOut {
//                 from { opacity: 1; transform: translateY(0); }
//                 to { opacity: 0; transform: translateY(-20px); }
//             }
//         `;
//         document.head.appendChild(style);
//     }
    
//     initSoundSystem() {
//         if (!this.soundInitialized) {
//             this.soundInitialized = true;
//             this.notificationSound = new Audio(this.settings.soundPath);
//             this.notificationSound.volume = 0.5;
            
//             // Try to get permission by playing/pausing immediately
//             this.notificationSound.play().then(() => {
//                 this.notificationSound.pause();
//                 this.notificationSound.currentTime = 0;
//             }).catch(() => {
//                 console.log("Notification sound initialization failed");
//             });
//         }
//     }
    
//     playNotificationSound() {
//         if (!this.settings.soundEnabled || !this.notificationSound) return;
        
//         try {
//             this.notificationSound.currentTime = 0;
//             // Create audio context if needed
//             if (!this.notificationSound.context) {
//                 try {
//                     const AudioContext = window.AudioContext || window.webkitAudioContext;
//                     this.notificationSound.context = new AudioContext();
//                     const source = this.notificationSound.context.createMediaElementSource(this.notificationSound);
//                     source.connect(this.notificationSound.context.destination);
//                 } catch (e) {
//                     console.log("Web Audio API not supported");
//                 }
//             }
            
//             // Play through Web Audio API if available
//             if (this.notificationSound.context) {
//                 this.notificationSound.context.resume().then(() => {
//                     this.notificationSound.play().catch(e => {
//                         console.log("Audio play blocked:", e);
//                     });
//                 });
//             } else {
//                 this.notificationSound.play().catch(e => {
//                     console.log("Audio play blocked:", e);
//                 });
//             }
//         } catch (e) {
//             console.log("Audio play error:", e);
//         }
//     }
    
//     initWebSocket() {
//         const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
//         this.notificationSocket = new WebSocket(`${wsScheme}://${window.location.host}/ws/notifications/`);
        
//         this.notificationSocket.onopen = () => console.log("Notification WebSocket connected");
        
//         this.notificationSocket.onmessage = (e) => {
//             const data = JSON.parse(e.data);
//             if (data.type === 'notification') {
//                 this.show({
//                     title: data.sender || 'New Message',
//                     message: data.message,
//                     link: `/chat/${data.room_id}/`,
//                     avatar: data.avatar || this.settings.avatarPath,
//                     sound: data.sound
//                 });
//             }
//         };
        
//         this.notificationSocket.onclose = () => console.log("Notification WebSocket closed");
//     }
    
//     show(notification) {
//         if (!this.container) {
//             console.error("Notification container not initialized");
//             return;
//         }
        
//         // Generate unique ID for each notification
//         const notificationId = 'notif-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        
//         // Limit number of notifications
//         if (this.notificationCount >= this.settings.maxNotifications) {
//             const oldestNotification = this.container.firstChild;
//             if (oldestNotification) {
//                 this.removeNotification(oldestNotification);
//             }
//         }
        
//         // Create notification element
//         const notificationElement = document.createElement('div');
//         notificationElement.id = notificationId;
//         notificationElement.className = `modern-notification ${this.settings.animation}-in`;
        
//         // Use sender's name if available, fallback to username
//         const title = notification.title || 'New Message';
        
//         // Avatar if enabled
//         const avatarHtml = this.settings.showAvatar ? 
//             `<img src="${notification.avatar}" alt="Avatar" class="notification-avatar">` : '';
        
//         // Close button if enabled
//         const closeButtonHtml = this.settings.showCloseButton ? 
//             `<button class="notification-close" data-notification-id="${notificationId}">&times;</button>` : '';
        
//         notificationElement.innerHTML = `
//             ${avatarHtml}
//             <div class="notification-content">
//                 <div class="notification-title">${title}</div>
//                 <div class="notification-message">${notification.message}</div>
//                 <div class="notification-actions">
//                     <a href="${notification.link}" class="notification-link">View</a>
//                 </div>
//             </div>
//             ${closeButtonHtml}
//             <div class="notification-progress"><div class="notification-progress-bar"></div></div>
//         `;
        
//         // Add to container
//         this.container.appendChild(notificationElement);
//         this.notificationCount++;
        
//         // Auto-remove after duration
//         const autoRemoveTimeout = setTimeout(() => {
//             this.removeNotification(notificationElement);
//             this.activeTimeouts.delete(notificationId);
//         }, this.settings.duration);
        
//         // Store timeout reference
//         this.activeTimeouts.set(notificationId, autoRemoveTimeout);
        
//         // Close button functionality
//         const closeButton = notificationElement.querySelector('.notification-close');
//         if (closeButton) {
//             closeButton.addEventListener('click', (e) => {
//                 e.stopPropagation();
//                 clearTimeout(this.activeTimeouts.get(notificationId));
//                 this.activeTimeouts.delete(notificationId);
//                 this.removeNotification(notificationElement);
//             });
//         }
        
//         // Click on notification to go to link
//         if (notification.link) {
//             notificationElement.addEventListener('click', (e) => {
//                 if (!e.target.classList.contains('notification-close') && 
//                     e.target.tagName !== 'BUTTON' && 
//                     e.target.tagName !== 'A') {
//                     window.location.href = notification.link;
//                 }
//             });
//         }
        
//         // Play sound if window is not focused
//         if (!this.isWindowFocused && this.settings.soundEnabled && notification.sound !== false) {
//             this.playNotificationSound();
//         }
        
//         // Fallback to browser notifications
//         if (!this.isWindowFocused && "Notification" in window && Notification.permission === "granted") {
//             new Notification(title, {
//                 body: notification.message,
//                 icon: notification.avatar || '/static/images/logo.png',
//                 silent: true
//             });
//         }
//     }
    
//     removeNotification(element) {
//         if (!element) return;
        
//         element.classList.add('fade-out');
//         element.addEventListener('animationend', () => {
//             element.remove();
//             this.notificationCount--;
//         }, { once: true });
//     }
    
//     updateSettings(newSettings) {
//         this.settings = {...this.settings, ...newSettings};
        
//         if (newSettings.position && this.container) {
//             this.container.className = `modern-notifier ${this.settings.position}`;
//         }
        
//         if (newSettings.soundEnabled && !this.soundInitialized) {
//             this.initSoundSystem();
//         }
//     }
// }

// // Initialize notifier with default settings
// const notifier = new ModernNotifier({
//     position: 'top-right',
//     animation: 'slide',
//     duration: 5000,
//     soundEnabled: true,
//     showCloseButton: true,
//     showAvatar: true
// });






