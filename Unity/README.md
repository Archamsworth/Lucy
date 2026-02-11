# Unity Project Setup for Lucy

This directory contains the Unity assets for the Lucy Virtual Companion project.

## Quick Start

### 1. Open Project

1. Open Unity Hub
2. Click "Add" or "Open"
3. Navigate to this `Unity` directory
4. Select and open

### 2. Install Dependencies

#### UniVRM (Required)
1. Download from: https://github.com/vrm-c/UniVRM/releases
2. In Unity: Assets → Import Package → Custom Package
3. Select the downloaded `.unitypackage`
4. Import all assets

#### Newtonsoft JSON (Required)
1. In Unity: Window → Package Manager
2. Click "+" → Add package from git URL
3. Enter: `com.unity.nuget.newtonsoft-json`
4. Click "Add"

### 3. Import Your VRM Avatar

1. Drag your `.vrm` file into the Assets folder
2. Wait for import to complete
3. Find the prefab in Project window
4. Drag into scene

### 4. Setup Scene

See `docs/SETUP.md` for detailed scene configuration instructions.

## Project Structure

```
Unity/
├── Assets/
│   ├── Scripts/
│   │   ├── VirtualCompanionController.cs  # Main controller
│   │   ├── UI/
│   │   │   └── UIManager.cs               # UI management
│   │   ├── Avatar/
│   │   │   ├── ExpressionController.cs    # Facial expressions
│   │   │   └── IdleAnimationController.cs # Idle animations
│   │   └── Audio/
│   │       └── MicrophoneRecorder.cs      # Microphone input
│   ├── Resources/
│   │   └── config.json                     # Configuration
│   ├── Scenes/
│   │   └── MainScene.unity                 # Main scene (create)
│   └── Materials/                          # Your materials
├── ProjectSettings/                        # Unity project settings
└── Packages/                               # Package manifest

```

## Scripts Overview

### VirtualCompanionController.cs
**Main orchestrator for the system**

Features:
- State machine (Idle → Listening → Processing → Speaking)
- HTTP communication with backend
- Audio playback
- Event system for UI updates

Usage:
```csharp
lucy.SendMessage("Hello!");
lucy.SendSpeech(audioClip);
lucy.ClearConversation();
```

### ExpressionController.cs
**Manages VRM facial expressions**

Features:
- Queue-based expression system
- Smooth transitions between expressions
- Maps expression strings to VRM blend shapes
- Automatic return to neutral

Expression Mapping:
- smile, happy, giggle → Joy
- sad, pout, shy → Sorrow
- angry → Angry
- surprised → Surprised
- thinking → Neutral

### IdleAnimationController.cs
**Provides natural idle behavior**

Features:
- Automatic blinking (every 3-5 seconds)
- Breathing animation (chest movement)
- Random head movements
- Configurable parameters

### UIManager.cs
**Handles all UI elements**

Features:
- Text input field
- Microphone button
- Chat history display
- Status messages
- Loading indicators

### MicrophoneRecorder.cs
**Records audio from microphone**

Features:
- Start/stop recording
- Configurable sample rate (16kHz default)
- Auto-trim recordings
- Permission handling

## Configuration

Edit `Assets/Resources/config.json`:

```json
{
  "backendURL": "http://localhost:8000",
  "micSampleRate": 16000,
  "maxRecordingLength": 30,
  "idleAnimationInterval": 3.0,
  "expressionDuration": 2.0,
  "expressionTransitionSpeed": 5.0
}
```

## Creating the Main Scene

### Step 1: Create New Scene
1. File → New Scene
2. Save as `MainScene` in `Assets/Scenes/`

### Step 2: Add Avatar
1. Drag VRM prefab into Hierarchy
2. Position at (0, 0, 0)
3. Verify Animator and VRMBlendShapeProxy are present

### Step 3: Add Controllers
1. Create Empty GameObject: "LucySystem"
2. Add Components:
   - VirtualCompanionController
   - ExpressionController
   - IdleAnimationController

3. Configure VirtualCompanionController:
   - API Base URL: `http://localhost:8000`
   - User ID: `default`
   - Expression Controller: (drag from same GameObject)
   - Audio Source: (auto-created)

4. Configure ExpressionController:
   - Blend Shape Proxy: (drag from VRM avatar)
   - Animator: (drag from VRM avatar)
   - Expression Duration: 2.0
   - Transition Speed: 5.0

5. Configure IdleAnimationController:
   - Enable Breathing: ✓
   - Enable Head Movement: ✓
   - Chest Bone: (find in VRM skeleton → Chest or Spine)
   - Head Bone: (find in VRM skeleton → Head)

### Step 4: Create UI
1. GameObject → UI → Canvas
   - Canvas Scaler: Scale With Screen Size
   - Reference Resolution: 1920x1080

2. Add UI Elements (as children of Canvas):

   **Input Field:**
   - GameObject → UI → Input Field (TextMeshPro)
   - Name: "MessageInput"
   - Position: Bottom of screen
   - Placeholder: "Type your message..."

   **Send Button:**
   - GameObject → UI → Button (TextMeshPro)
   - Name: "SendButton"
   - Text: "Send"
   - Position: Right of input field

   **Mic Button:**
   - GameObject → UI → Button (TextMeshPro)
   - Name: "MicButton"
   - Text: "🎤 Mic"
   - Position: Left of input field

   **Clear Button:**
   - GameObject → UI → Button (TextMeshPro)
   - Name: "ClearButton"
   - Text: "Clear"
   - Position: Top right

   **Chat History:**
   - GameObject → UI → Text (TextMeshPro)
   - Name: "ChatHistory"
   - Position: Center-left of screen
   - Enable: Rich Text, Auto Size

   **Status Text:**
   - GameObject → UI → Text (TextMeshPro)
   - Name: "StatusText"
   - Position: Bottom left
   - Text: "Ready"

   **Loading Indicator:**
   - GameObject → UI → Image
   - Name: "LoadingIndicator"
   - Add: Spinner animation or dots
   - Initially: Disabled

### Step 5: Connect UI Manager
1. Add UIManager script to Canvas
2. Assign all UI elements in Inspector:
   - Message Input → MessageInput
   - Send Button → SendButton
   - Mic Button → MicButton
   - Clear Button → ClearButton
   - Chat History Text → ChatHistory
   - Status Text → StatusText
   - Loading Indicator → LoadingIndicator
   - Controller → LucySystem/VirtualCompanionController

### Step 6: Camera Setup
1. Position Main Camera to frame avatar
2. Typical position: (0, 1.5, 3)
3. Rotation: (0, 0, 0)

### Step 7: Lighting
1. Add Directional Light if needed
2. Optional: Skybox for background

## Testing in Unity

### Play Mode Test
1. Ensure backend and LLM server are running
2. Click Play button
3. Type message in input field
4. Click Send
5. Observe:
   - Status changes
   - Avatar expressions
   - Audio playback
   - Response in chat

### Debug Console
Watch for:
- State changes logged
- Network requests
- Errors or warnings

### Common Issues

**"No animator assigned"**
- Solution: Drag Animator from VRM avatar to ExpressionController

**"VRMBlendShapeProxy not found"**
- Solution: Ensure VRM model is properly imported and has VRMBlendShapeProxy component

**"Connection refused"**
- Solution: Check backend URL in VirtualCompanionController
- Verify backend is running: `curl http://localhost:8000/health`

**"Microphone not detected"**
- Solution: Grant microphone permissions to Unity
- Check: System Settings → Privacy → Microphone

**No expressions showing**
- Solution: Check VRM model has blend shapes
- Verify ExpressionController is properly configured

## Building

### Windows Build
1. File → Build Settings
2. Select "Windows, Mac, Linux"
3. Platform: Windows
4. Architecture: x86_64
5. Click "Build"

### Standalone Configuration
Ensure backend is accessible:
- Use IP address instead of localhost if needed
- Configure firewall to allow connections
- Update backendURL in config.json

## Performance Tips

### Optimize Avatar
- Use < 50K polygons
- Limit blend shapes to essentials
- Compress textures

### Optimize UI
- Use sprite atlases
- Minimize draw calls
- Pool UI elements if creating dynamically

### Optimize Scripts
- Cache component references
- Avoid GetComponent in Update
- Use object pooling for audio

## Extending the System

### Add Custom Expressions
1. Add to `ExpressionController.expressionBlendShapeMap`
2. Update backend `SUPPORTED_EXPRESSIONS`
3. Train LLM to use new expression

### Add Gestures/Animations
1. Create animation clips in Unity
2. Add to Animator Controller
3. Trigger from VirtualCompanionController

### Add Custom UI
1. Extend UIManager
2. Add new UI elements
3. Connect to events

## Resources

- **UniVRM Documentation:** https://vrm.dev/en/univrm/
- **Unity Documentation:** https://docs.unity3d.com/
- **TextMeshPro:** https://docs.unity3d.com/Packages/com.unity.textmeshpro@3.0/
- **Unity UI:** https://docs.unity3d.com/Packages/com.unity.ugui@1.0/

## Support

For issues:
1. Check Unity Console for errors
2. Review `docs/TESTING.md`
3. Verify backend connectivity
4. Check component assignments

---

Happy building! 🎭
