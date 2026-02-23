using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using Newtonsoft.Json;

namespace Lucy
{
    /// <summary>
    /// Continuously listens for a wake word phrase ("hey lucy", etc.)
    /// by sending short audio chunks to the backend /wake endpoint.
    ///
    /// When the wake word is detected an event is raised so other
    /// components (e.g. UIManager) can start full speech recording.
    /// </summary>
    public class WakeWordListener : MonoBehaviour
    {
        [Header("Configuration")]
        [SerializeField] private string apiBaseUrl = "http://localhost:8000";

        [Header("Recording Settings")]
        [Tooltip("Length of each audio chunk sent for wake-word detection (seconds)")]
        [SerializeField] private float chunkDuration = 2.5f;

        [Tooltip("Sample rate used for recording (must match Whisper expectation)")]
        [SerializeField] private int sampleRate = 16000;

        [Tooltip("Pause between chunks when NOT actively listening (seconds)")]
        [SerializeField] private float pollInterval = 0.5f;

        [Header("State")]
        [SerializeField] private bool isListening = false;

        // Event fired when a wake word is detected in a chunk
        public event Action OnWakeWordDetected;

        private Coroutine _listenLoop;

        // ------------------------------------------------------------------
        // Unity lifecycle
        // ------------------------------------------------------------------

        void Start()
        {
            if (Microphone.devices.Length == 0)
            {
                Debug.LogWarning("WakeWordListener: No microphone detected. Wake word will be unavailable.");
                enabled = false;
                return;
            }

            StartListening();
        }

        void OnDestroy()
        {
            StopListening();
        }

        // ------------------------------------------------------------------
        // Public control API
        // ------------------------------------------------------------------

        /// <summary>Start continuous wake-word detection</summary>
        public void StartListening()
        {
            if (isListening) return;

            isListening = true;
            _listenLoop = StartCoroutine(WakeWordLoop());
            Debug.Log("WakeWordListener: started");
        }

        /// <summary>Stop continuous wake-word detection</summary>
        public void StopListening()
        {
            if (!isListening) return;

            isListening = false;
            if (_listenLoop != null)
            {
                StopCoroutine(_listenLoop);
                _listenLoop = null;
            }

            Microphone.End(null);
            Debug.Log("WakeWordListener: stopped");
        }

        /// <summary>Returns true while the listener is running</summary>
        public bool IsListening => isListening;

        // ------------------------------------------------------------------
        // Detection loop
        // ------------------------------------------------------------------

        private IEnumerator WakeWordLoop()
        {
            while (isListening)
            {
                // null device name = Unity default microphone (documented choice)
                AudioClip chunk = Microphone.Start(null, false, Mathf.CeilToInt(chunkDuration), sampleRate);

                // Wait for the chunk to fill
                yield return new WaitForSeconds(chunkDuration);

                // null = stop the default microphone (matches what Start used)
                Microphone.End(null);

                // Convert to WAV bytes
                byte[] wavData = AudioClipToWav(chunk);

                // Send to backend and wait for result
                yield return StartCoroutine(SendChunkToBackend(wavData));

                // Brief pause before next chunk
                yield return new WaitForSeconds(pollInterval);
            }
        }

        private IEnumerator SendChunkToBackend(byte[] wavData)
        {
            WWWForm form = new WWWForm();
            form.AddBinaryData("audio", wavData, "wake_chunk.wav", "audio/wav");

            using (UnityWebRequest www = UnityWebRequest.Post($"{apiBaseUrl}/wake", form))
            {
                yield return www.SendWebRequest();

                if (www.result == UnityWebRequest.Result.Success)
                {
                    WakeResponse resp = JsonConvert.DeserializeObject<WakeResponse>(www.downloadHandler.text);

                    if (resp != null && resp.wake_word_detected)
                    {
                        Debug.Log($"WakeWordListener: wake word detected in '{resp.transcription}'");
                        OnWakeWordDetected?.Invoke();
                    }
                }
                else
                {
                    // Non-fatal: backend may be unreachable or STT unavailable
                    Debug.LogWarning($"WakeWordListener: backend error - {www.error}");
                }
            }
        }

        // ------------------------------------------------------------------
        // WAV encoding helper
        // ------------------------------------------------------------------

        private byte[] AudioClipToWav(AudioClip clip)
        {
            if (clip == null) return new byte[0];

            float[] samples = new float[clip.samples * clip.channels];
            clip.GetData(samples, 0);

            short[] pcm = new short[samples.Length];
            for (int i = 0; i < samples.Length; i++)
            {
                pcm[i] = (short)Mathf.Clamp((int)(samples[i] * 32767), short.MinValue, short.MaxValue);
            }

            int sRate = clip.frequency;
            int channels = clip.channels;
            int byteRate = sRate * channels * 2;

            using (System.IO.MemoryStream ms = new System.IO.MemoryStream())
            using (System.IO.BinaryWriter bw = new System.IO.BinaryWriter(ms))
            {
                // RIFF header
                bw.Write(System.Text.Encoding.ASCII.GetBytes("RIFF"));
                bw.Write(36 + pcm.Length * 2);
                bw.Write(System.Text.Encoding.ASCII.GetBytes("WAVE"));

                // fmt chunk
                bw.Write(System.Text.Encoding.ASCII.GetBytes("fmt "));
                bw.Write(16);
                bw.Write((short)1);        // PCM
                bw.Write((short)channels);
                bw.Write(sRate);
                bw.Write(byteRate);
                bw.Write((short)(channels * 2));
                bw.Write((short)16);       // bits per sample

                // data chunk
                bw.Write(System.Text.Encoding.ASCII.GetBytes("data"));
                bw.Write(pcm.Length * 2);
                foreach (short s in pcm) bw.Write(s);

                return ms.ToArray();
            }
        }

        // ------------------------------------------------------------------
        // Data models
        // ------------------------------------------------------------------

        [Serializable]
        private class WakeResponse
        {
            public bool wake_word_detected;
            public string transcription;
        }
    }
}
