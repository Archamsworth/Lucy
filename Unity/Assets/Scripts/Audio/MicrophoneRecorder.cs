using UnityEngine;

namespace Lucy
{
    /// <summary>
    /// Records microphone input for speech-to-text
    /// </summary>
    public class MicrophoneRecorder : MonoBehaviour
    {
        [Header("Recording Settings")]
        [SerializeField] private int recordingLength = 30; // Maximum recording length in seconds
        [SerializeField] private int sampleRate = 16000; // 16kHz for speech recognition
        [SerializeField] private string microphoneDevice = null; // null = default microphone
        
        private AudioClip recordingClip;
        private bool isRecording = false;
        private float recordingStartTime;
        
        /// <summary>
        /// Start recording from microphone
        /// </summary>
        public void StartRecording()
        {
            if (isRecording)
            {
                Debug.LogWarning("Already recording");
                return;
            }
            
            // Check if microphone is available
            if (Microphone.devices.Length == 0)
            {
                Debug.LogError("No microphone detected!");
                return;
            }
            
            // Use specified device or default
            string device = microphoneDevice;
            if (string.IsNullOrEmpty(device) && Microphone.devices.Length > 0)
            {
                device = Microphone.devices[0];
                Debug.Log($"Using microphone: {device}");
            }
            
            // Start recording
            recordingClip = Microphone.Start(device, false, recordingLength, sampleRate);
            isRecording = true;
            recordingStartTime = Time.time;
            
            Debug.Log("Recording started");
        }
        
        /// <summary>
        /// Stop recording and return the AudioClip
        /// </summary>
        public AudioClip StopRecording()
        {
            if (!isRecording)
            {
                Debug.LogWarning("Not currently recording");
                return null;
            }
            
            // Stop recording
            Microphone.End(microphoneDevice);
            isRecording = false;
            
            float recordingDuration = Time.time - recordingStartTime;
            Debug.Log($"Recording stopped. Duration: {recordingDuration:F2}s");
            
            // Trim the audio clip to actual recorded length
            if (recordingClip != null && recordingDuration < recordingLength)
            {
                recordingClip = TrimAudioClip(recordingClip, recordingDuration);
            }
            
            return recordingClip;
        }
        
        /// <summary>
        /// Check if currently recording
        /// </summary>
        public bool IsRecording()
        {
            return isRecording;
        }
        
        /// <summary>
        /// Get list of available microphone devices
        /// </summary>
        public static string[] GetMicrophoneDevices()
        {
            return Microphone.devices;
        }
        
        /// <summary>
        /// Trim audio clip to specified duration
        /// </summary>
        private AudioClip TrimAudioClip(AudioClip clip, float duration)
        {
            if (clip == null) return null;
            
            int samples = Mathf.CeilToInt(duration * clip.frequency);
            samples = Mathf.Min(samples, clip.samples);
            
            float[] data = new float[samples * clip.channels];
            clip.GetData(data, 0);
            
            AudioClip trimmedClip = AudioClip.Create(
                "TrimmedRecording",
                samples,
                clip.channels,
                clip.frequency,
                false
            );
            
            trimmedClip.SetData(data, 0);
            
            return trimmedClip;
        }
        
        void OnDestroy()
        {
            // Stop recording if still active
            if (isRecording)
            {
                Microphone.End(microphoneDevice);
            }
        }
    }
}
