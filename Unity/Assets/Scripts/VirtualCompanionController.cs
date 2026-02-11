using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using Newtonsoft.Json;

namespace Lucy
{
    /// <summary>
    /// Main controller for Lucy AI Virtual Companion
    /// Orchestrates all components and manages conversation flow
    /// </summary>
    public class VirtualCompanionController : MonoBehaviour
    {
        [Header("Configuration")]
        [SerializeField] private string apiBaseUrl = "http://localhost:8000";
        [SerializeField] private string userId = "default";
        
        [Header("Components")]
        [SerializeField] private ExpressionController expressionController;
        [SerializeField] private AudioSource audioSource;
        
        [Header("Settings")]
        [SerializeField] private float temperature = 0.8f;
        [SerializeField] private int maxTokens = 200;
        
        // State machine
        public enum CompanionState
        {
            Idle,
            Listening,
            Processing,
            Speaking
        }
        
        private CompanionState currentState = CompanionState.Idle;
        
        // Events
        public event Action<string> OnMessageSent;
        public event Action<CompanionResponse> OnResponseReceived;
        public event Action<string> OnError;
        public event Action<CompanionState> OnStateChanged;
        
        void Start()
        {
            if (audioSource == null)
            {
                audioSource = gameObject.AddComponent<AudioSource>();
            }
            
            SetState(CompanionState.Idle);
        }
        
        /// <summary>
        /// Send text message to Lucy
        /// </summary>
        public void SendMessage(string message)
        {
            if (string.IsNullOrWhiteSpace(message))
            {
                Debug.LogWarning("Cannot send empty message");
                return;
            }
            
            if (currentState != CompanionState.Idle)
            {
                Debug.LogWarning($"Cannot send message while in {currentState} state");
                return;
            }
            
            StartCoroutine(SendTextMessageCoroutine(message));
        }
        
        /// <summary>
        /// Send speech audio to Lucy
        /// </summary>
        public void SendSpeech(AudioClip audioClip)
        {
            if (audioClip == null)
            {
                Debug.LogWarning("Cannot send null audio clip");
                return;
            }
            
            if (currentState != CompanionState.Idle)
            {
                Debug.LogWarning($"Cannot send speech while in {currentState} state");
                return;
            }
            
            StartCoroutine(SendSpeechMessageCoroutine(audioClip));
        }
        
        /// <summary>
        /// Clear conversation history
        /// </summary>
        public void ClearConversation()
        {
            StartCoroutine(ClearConversationCoroutine());
        }
        
        private IEnumerator SendTextMessageCoroutine(string message)
        {
            SetState(CompanionState.Processing);
            OnMessageSent?.Invoke(message);
            
            var request = new ChatRequest
            {
                user_id = userId,
                message = message,
                temperature = temperature,
                max_tokens = maxTokens
            };
            
            string jsonData = JsonConvert.SerializeObject(request);
            
            using (UnityWebRequest www = new UnityWebRequest($"{apiBaseUrl}/chat", "POST"))
            {
                byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
                www.uploadHandler = new UploadHandlerRaw(bodyRaw);
                www.downloadHandler = new DownloadHandlerBuffer();
                www.SetRequestHeader("Content-Type", "application/json");
                
                yield return www.SendWebRequest();
                
                if (www.result == UnityWebRequest.Result.Success)
                {
                    string response = www.downloadHandler.text;
                    CompanionResponse companionResponse = JsonConvert.DeserializeObject<CompanionResponse>(response);
                    
                    OnResponseReceived?.Invoke(companionResponse);
                    yield return ProcessResponse(companionResponse);
                }
                else
                {
                    string error = $"Error sending message: {www.error}";
                    Debug.LogError(error);
                    OnError?.Invoke(error);
                    SetState(CompanionState.Idle);
                }
            }
        }
        
        private IEnumerator SendSpeechMessageCoroutine(AudioClip audioClip)
        {
            SetState(CompanionState.Listening);
            
            // Convert AudioClip to WAV bytes
            byte[] wavData = ConvertAudioClipToWav(audioClip);
            
            SetState(CompanionState.Processing);
            
            WWWForm form = new WWWForm();
            form.AddBinaryData("audio", wavData, "audio.wav", "audio/wav");
            form.AddField("user_id", userId);
            form.AddField("temperature", temperature.ToString());
            form.AddField("max_tokens", maxTokens);
            
            using (UnityWebRequest www = UnityWebRequest.Post($"{apiBaseUrl}/speech", form))
            {
                yield return www.SendWebRequest();
                
                if (www.result == UnityWebRequest.Result.Success)
                {
                    string response = www.downloadHandler.text;
                    CompanionResponse companionResponse = JsonConvert.DeserializeObject<CompanionResponse>(response);
                    
                    OnResponseReceived?.Invoke(companionResponse);
                    yield return ProcessResponse(companionResponse);
                }
                else
                {
                    string error = $"Error sending speech: {www.error}";
                    Debug.LogError(error);
                    OnError?.Invoke(error);
                    SetState(CompanionState.Idle);
                }
            }
        }
        
        private IEnumerator ProcessResponse(CompanionResponse response)
        {
            SetState(CompanionState.Speaking);
            
            // Trigger expressions
            if (expressionController != null && response.expressions != null)
            {
                foreach (string expression in response.expressions)
                {
                    expressionController.TriggerExpression(expression);
                }
            }
            
            // Play audio if available
            if (!string.IsNullOrEmpty(response.audio_url))
            {
                yield return PlayAudio(response.audio_url);
            }
            else
            {
                // If no audio, wait for a bit based on text length
                float duration = Mathf.Max(2f, response.text.Length * 0.05f);
                yield return new WaitForSeconds(duration);
            }
            
            SetState(CompanionState.Idle);
        }
        
        private IEnumerator PlayAudio(string audioUrl)
        {
            string fullUrl = audioUrl.StartsWith("http") ? audioUrl : $"{apiBaseUrl}{audioUrl}";
            
            using (UnityWebRequest www = UnityWebRequestMultimedia.GetAudioClip(fullUrl, AudioType.WAV))
            {
                yield return www.SendWebRequest();
                
                if (www.result == UnityWebRequest.Result.Success)
                {
                    AudioClip clip = DownloadHandlerAudioClip.GetContent(www);
                    audioSource.clip = clip;
                    audioSource.Play();
                    
                    // Wait for audio to finish
                    yield return new WaitWhile(() => audioSource.isPlaying);
                }
                else
                {
                    Debug.LogWarning($"Could not load audio: {www.error}");
                }
            }
        }
        
        private IEnumerator ClearConversationCoroutine()
        {
            using (UnityWebRequest www = UnityWebRequest.Delete($"{apiBaseUrl}/conversation/{userId}"))
            {
                www.downloadHandler = new DownloadHandlerBuffer();
                yield return www.SendWebRequest();
                
                if (www.result == UnityWebRequest.Result.Success)
                {
                    Debug.Log("Conversation cleared");
                }
                else
                {
                    Debug.LogError($"Error clearing conversation: {www.error}");
                }
            }
        }
        
        private void SetState(CompanionState newState)
        {
            if (currentState != newState)
            {
                currentState = newState;
                OnStateChanged?.Invoke(currentState);
                Debug.Log($"State changed to: {currentState}");
            }
        }
        
        private byte[] ConvertAudioClipToWav(AudioClip clip)
        {
            // Simple WAV conversion for Unity AudioClip
            // Note: This is a basic implementation
            float[] samples = new float[clip.samples * clip.channels];
            clip.GetData(samples, 0);
            
            // Convert to 16-bit PCM
            short[] intData = new short[samples.Length];
            for (int i = 0; i < samples.Length; i++)
            {
                intData[i] = (short)(samples[i] * 32767);
            }
            
            // Create WAV file
            int sampleRate = clip.frequency;
            int channels = clip.channels;
            int byteRate = sampleRate * channels * 2;
            
            using (System.IO.MemoryStream stream = new System.IO.MemoryStream())
            using (System.IO.BinaryWriter writer = new System.IO.BinaryWriter(stream))
            {
                // RIFF header
                writer.Write("RIFF".ToCharArray());
                writer.Write(36 + intData.Length * 2);
                writer.Write("WAVE".ToCharArray());
                
                // fmt chunk
                writer.Write("fmt ".ToCharArray());
                writer.Write(16);
                writer.Write((short)1); // PCM
                writer.Write((short)channels);
                writer.Write(sampleRate);
                writer.Write(byteRate);
                writer.Write((short)(channels * 2));
                writer.Write((short)16); // bits per sample
                
                // data chunk
                writer.Write("data".ToCharArray());
                writer.Write(intData.Length * 2);
                
                foreach (short sample in intData)
                {
                    writer.Write(sample);
                }
                
                return stream.ToArray();
            }
        }
        
        // Data models
        [Serializable]
        private class ChatRequest
        {
            public string user_id;
            public string message;
            public float temperature;
            public int max_tokens;
        }
    }
    
    [Serializable]
    public class CompanionResponse
    {
        public List<string> expressions;
        public string text;
        public string audio_url;
        public string raw_response;
    }
}
