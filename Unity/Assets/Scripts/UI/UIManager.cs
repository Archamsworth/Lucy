using UnityEngine;
using UnityEngine.UI;
using TMPro;

namespace Lucy
{
    /// <summary>
    /// Manages UI elements for Lucy Virtual Companion
    /// </summary>
    public class UIManager : MonoBehaviour
    {
        [Header("UI References")]
        [SerializeField] private TMP_InputField messageInput;
        [SerializeField] private Button sendButton;
        [SerializeField] private Button micButton;
        [SerializeField] private Button clearButton;
        [SerializeField] private TextMeshProUGUI chatHistoryText;
        [SerializeField] private GameObject loadingIndicator;
        [SerializeField] private TextMeshProUGUI statusText;
        
        [Header("Controller")]
        [SerializeField] private VirtualCompanionController controller;
        
        private bool isRecording = false;
        private MicrophoneRecorder micRecorder;
        
        void Start()
        {
            // Setup button listeners
            if (sendButton != null)
            {
                sendButton.onClick.AddListener(OnSendButtonClicked);
            }
            
            if (micButton != null)
            {
                micButton.onClick.AddListener(OnMicButtonClicked);
            }
            
            if (clearButton != null)
            {
                clearButton.onClick.AddListener(OnClearButtonClicked);
            }
            
            // Setup input field
            if (messageInput != null)
            {
                messageInput.onSubmit.AddListener(OnMessageSubmit);
            }
            
            // Get or create microphone recorder
            micRecorder = GetComponent<MicrophoneRecorder>();
            if (micRecorder == null)
            {
                micRecorder = gameObject.AddComponent<MicrophoneRecorder>();
            }

            // Wire up wake word listener if present on the same GameObject
            WakeWordListener wakeListener = GetComponent<WakeWordListener>();
            if (wakeListener != null)
            {
                wakeListener.OnWakeWordDetected += OnWakeWordDetected;
            }

            // Subscribe to controller events
            if (controller != null)
            {
                controller.OnMessageSent += OnMessageSent;
                controller.OnResponseReceived += OnResponseReceived;
                controller.OnError += OnError;
                controller.OnStateChanged += OnStateChanged;
            }
            
            // Initialize UI
            if (loadingIndicator != null)
            {
                loadingIndicator.SetActive(false);
            }
            
            UpdateStatusText("Ready");
        }
        
        void OnDestroy()
        {
            // Unsubscribe from events
            if (controller != null)
            {
                controller.OnMessageSent -= OnMessageSent;
                controller.OnResponseReceived -= OnResponseReceived;
                controller.OnError -= OnError;
                controller.OnStateChanged -= OnStateChanged;
            }

            WakeWordListener wakeListener = GetComponent<WakeWordListener>();
            if (wakeListener != null)
            {
                wakeListener.OnWakeWordDetected -= OnWakeWordDetected;
            }
        }
        
        private void OnSendButtonClicked()
        {
            SendCurrentMessage();
        }
        
        private void OnMessageSubmit(string message)
        {
            SendCurrentMessage();
        }
        
        private void SendCurrentMessage()
        {
            if (messageInput == null || controller == null) return;
            
            string message = messageInput.text.Trim();
            
            if (string.IsNullOrEmpty(message))
            {
                Debug.LogWarning("Cannot send empty message");
                return;
            }
            
            controller.SendMessage(message);
            messageInput.text = "";
            messageInput.ActivateInputField();
        }
        
        private void OnMicButtonClicked()
        {
            if (isRecording)
            {
                StopRecording();
            }
            else
            {
                StartRecording();
            }
        }
        
        private void StartRecording()
        {
            if (micRecorder == null) return;
            
            isRecording = true;
            micRecorder.StartRecording();
            
            // Update UI
            if (micButton != null)
            {
                var buttonText = micButton.GetComponentInChildren<TextMeshProUGUI>();
                if (buttonText != null)
                {
                    buttonText.text = "⏹ Stop";
                }
            }
            
            UpdateStatusText("Listening...");
        }
        
        private void StopRecording()
        {
            if (micRecorder == null) return;
            
            AudioClip clip = micRecorder.StopRecording();
            isRecording = false;
            
            // Update UI
            if (micButton != null)
            {
                var buttonText = micButton.GetComponentInChildren<TextMeshProUGUI>();
                if (buttonText != null)
                {
                    buttonText.text = "🎤 Mic";
                }
            }
            
            // Send audio to controller
            if (clip != null && controller != null)
            {
                controller.SendSpeech(clip);
            }
        }
        
        private void OnClearButtonClicked()
        {
            if (controller != null)
            {
                controller.ClearConversation();
            }
            
            if (chatHistoryText != null)
            {
                chatHistoryText.text = "";
            }
            
            UpdateStatusText("Conversation cleared");
        }
        
        private void OnMessageSent(string message)
        {
            AppendToChatHistory($"You: {message}");
        }
        
        private void OnResponseReceived(CompanionResponse response)
        {
            AppendToChatHistory($"Lucy: {response.text}");
        }
        
        private void OnError(string error)
        {
            UpdateStatusText($"Error: {error}");
            Debug.LogError(error);
        }
        
        private void OnStateChanged(VirtualCompanionController.CompanionState state)
        {
            // Update UI based on state
            bool isProcessing = state != VirtualCompanionController.CompanionState.Idle;
            
            if (loadingIndicator != null)
            {
                loadingIndicator.SetActive(isProcessing);
            }
            
            // Disable input while processing
            if (sendButton != null)
            {
                sendButton.interactable = !isProcessing;
            }
            
            if (messageInput != null)
            {
                messageInput.interactable = !isProcessing;
            }
            
            // Update status text
            switch (state)
            {
                case VirtualCompanionController.CompanionState.Idle:
                    UpdateStatusText("Ready");
                    break;
                case VirtualCompanionController.CompanionState.Listening:
                    UpdateStatusText("Listening...");
                    break;
                case VirtualCompanionController.CompanionState.Processing:
                    UpdateStatusText("Processing...");
                    break;
                case VirtualCompanionController.CompanionState.Speaking:
                    UpdateStatusText("Lucy is speaking...");
                    break;
            }
        }
        
        private void AppendToChatHistory(string message)
        {
            if (chatHistoryText == null) return;
            
            if (!string.IsNullOrEmpty(chatHistoryText.text))
            {
                chatHistoryText.text += "\n\n";
            }
            
            chatHistoryText.text += message;
        }
        
        private void UpdateStatusText(string status)
        {
            if (statusText != null)
            {
                statusText.text = status;
            }
        }

        /// <summary>
        /// Called by WakeWordListener when the wake phrase is detected.
        /// Automatically starts microphone recording so the user can speak.
        /// </summary>
        private void OnWakeWordDetected()
        {
            UpdateStatusText("Wake word detected! Listening...");
            StartRecording();
        }
    }
}
