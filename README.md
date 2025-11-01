# LiveChat - Real-time Communication Platform

![Django](https://img.shields.io/badge/Django-5.2.7-green)
![Channels](https://img.shields.io/badge/Channels-4.3.1-blue)
![WebRTC](https://img.shields.io/badge/WebRTC-Enabled-orange)

LiveChat is a comprehensive communication platform inspired by WhatsApp, offering real-time chat and video calling capabilities, with audio calling coming soon.

## Features

### Real-time Communication
- **Text Chat**
  - Instant message delivery
  - Message history
  - Read receipts
  - Online status indicators

- **Video Calling**
  - One-on-one video calls
  - High-quality video streaming
  - Screen sharing capability
  - Camera switch support

- **Coming Soon**
  - Audio calling
  - Group video calls
  - Call recording
  - Background blur effects

### User Features
- **Authentication & Security**
  - Secure login/signup
  - Profile customization
  - Privacy settings
  - Session management

- **Profile Management**
  - Custom display pictures
  - Status updates
  - User preferences
  - Activity status

## Technical Stack

### Frontend
- WebRTC for video calls
- WebSocket for real-time communication
- Responsive UI design
- Media handling capabilities

### Backend
- Django 5.2.7
- Django Channels for WebSocket
- STUN/TURN servers for video calls
- PostgreSQL database

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/LiveChat.git
   cd LiveChat

2. Set up virtual environment
   
   ```bash
   python -m venv venv
   venv\Scripts\activate
    ```
3. Install dependencies
   
   ```bash
   pip install -r requirements.txt
    ```
4. Run migrations
   
   ```bash
   python manage.py migrate
    ```
## Usage
### Chat Features
- Start a new chat by selecting a contact
- Send text messages, emojis, and files
- View message status (sent/delivered/read)
### Video Calling
1. Select a contact
2. Click the video call icon
3. Wait for the recipient to accept
4. Grant camera and microphone permissions
### Upcoming Audio Calls
- One-to-one audio calls
- Group audio calls
- Voice message support
- Call forwarding
## Development Roadmap
### Phase 1 (Completed)
- ✅ Real-time chat implementation
- ✅ Video calling integration
- ✅ User authentication
- ✅ Profile management
### Phase 2 (In Progress)
- 🔄 Audio calling implementation
- 🔄 Group calling features
- 🔄 Call recording
- 🔄 Enhanced security features
### Phase 3 (Planned)
- 📋 End-to-end encryption
- 📋 File sharing improvements
- 📋 Status features
- 📋 Story sharing
## Contributing
We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Support
For support, please create an issue in the GitHub repository or contact the development team.

Note: This project is under active development. Audio calling features are currently being implemented and will be available in the next major release.

```plaintext

This updated README reflects the WhatsApp-like features of your application, highlighting the existing video calling capability and the upcoming audio calling feature. It provides a comprehensive overview of the current and planned functionality, making it clear to users and potential contributors what the platform offers and where it's heading.

Would you like me to add or modify any specific sections of the README?

```
