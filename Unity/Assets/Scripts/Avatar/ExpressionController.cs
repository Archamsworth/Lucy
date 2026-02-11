using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using VRM;

namespace Lucy
{
    /// <summary>
    /// Controls VRM avatar expressions and animations
    /// </summary>
    public class ExpressionController : MonoBehaviour
    {
        [Header("VRM Components")]
        [SerializeField] private VRMBlendShapeProxy blendShapeProxy;
        [SerializeField] private Animator animator;
        
        [Header("Expression Settings")]
        [SerializeField] private float expressionDuration = 2.0f;
        [SerializeField] private float transitionSpeed = 5.0f;
        [SerializeField] private bool queueExpressions = true;
        
        // Expression queue
        private Queue<string> expressionQueue = new Queue<string>();
        private bool isPlayingExpression = false;
        private string currentExpression = "";
        
        // Expression to BlendShape mapping
        private Dictionary<string, string> expressionBlendShapeMap = new Dictionary<string, string>()
        {
            { "smile", "Joy" },
            { "happy", "Joy" },
            { "giggle", "Joy" },
            { "laugh", "Joy" },
            { "smirk", "Fun" },
            { "excited", "Joy" },
            { "pout", "Sorrow" },
            { "sad", "Sorrow" },
            { "blush", "Joy" },
            { "shy", "Sorrow" },
            { "angry", "Angry" },
            { "surprised", "Surprised" },
            { "thinking", "Neutral" },
            { "worried", "Sorrow" },
            { "confused", "Surprised" }
        };
        
        void Start()
        {
            // Try to find VRM components if not assigned
            if (blendShapeProxy == null)
            {
                blendShapeProxy = GetComponentInChildren<VRMBlendShapeProxy>();
            }
            
            if (animator == null)
            {
                animator = GetComponentInChildren<Animator>();
            }
            
            if (blendShapeProxy == null)
            {
                Debug.LogWarning("VRMBlendShapeProxy not found. Expression system may not work properly.");
            }
            
            if (animator == null)
            {
                Debug.LogWarning("Animator not found. Animation triggers may not work.");
            }
        }
        
        void Update()
        {
            // Process expression queue
            if (!isPlayingExpression && expressionQueue.Count > 0)
            {
                string nextExpression = expressionQueue.Dequeue();
                StartCoroutine(PlayExpression(nextExpression));
            }
        }
        
        /// <summary>
        /// Trigger an expression
        /// </summary>
        public void TriggerExpression(string expressionName)
        {
            if (string.IsNullOrEmpty(expressionName))
            {
                return;
            }
            
            string normalizedExpression = expressionName.ToLower().Trim();
            
            if (queueExpressions)
            {
                expressionQueue.Enqueue(normalizedExpression);
            }
            else
            {
                // Immediate mode - interrupt current expression
                StopAllCoroutines();
                isPlayingExpression = false;
                StartCoroutine(PlayExpression(normalizedExpression));
            }
        }
        
        /// <summary>
        /// Clear expression queue
        /// </summary>
        public void ClearQueue()
        {
            expressionQueue.Clear();
        }
        
        /// <summary>
        /// Reset to neutral expression
        /// </summary>
        public void ResetToNeutral()
        {
            if (blendShapeProxy != null)
            {
                blendShapeProxy.ImmediatelySetValue(BlendShapePreset.Neutral, 1.0f);
                blendShapeProxy.ImmediatelySetValue(BlendShapePreset.Joy, 0f);
                blendShapeProxy.ImmediatelySetValue(BlendShapePreset.Angry, 0f);
                blendShapeProxy.ImmediatelySetValue(BlendShapePreset.Sorrow, 0f);
                blendShapeProxy.ImmediatelySetValue(BlendShapePreset.Fun, 0f);
                blendShapeProxy.ImmediatelySetValue(BlendShapePreset.Surprised, 0f);
            }
            
            currentExpression = "neutral";
        }
        
        private IEnumerator PlayExpression(string expressionName)
        {
            isPlayingExpression = true;
            currentExpression = expressionName;
            
            // Trigger animator if available
            if (animator != null && animator.runtimeAnimatorController != null)
            {
                animator.SetTrigger(expressionName);
            }
            
            // Apply VRM blend shape
            if (blendShapeProxy != null && expressionBlendShapeMap.ContainsKey(expressionName))
            {
                string blendShapeName = expressionBlendShapeMap[expressionName];
                BlendShapePreset preset = GetBlendShapePreset(blendShapeName);
                
                // Fade in expression
                float elapsed = 0f;
                float fadeInDuration = 0.3f;
                
                while (elapsed < fadeInDuration)
                {
                    elapsed += Time.deltaTime;
                    float value = Mathf.Lerp(0f, 1f, elapsed / fadeInDuration);
                    blendShapeProxy.ImmediatelySetValue(preset, value);
                    yield return null;
                }
                
                // Hold expression
                yield return new WaitForSeconds(expressionDuration - fadeInDuration * 2);
                
                // Fade out expression
                elapsed = 0f;
                
                while (elapsed < fadeInDuration)
                {
                    elapsed += Time.deltaTime;
                    float value = Mathf.Lerp(1f, 0f, elapsed / fadeInDuration);
                    blendShapeProxy.ImmediatelySetValue(preset, value);
                    yield return null;
                }
                
                // Reset to neutral
                ResetToNeutral();
            }
            else
            {
                // Just wait if no blend shape available
                yield return new WaitForSeconds(expressionDuration);
            }
            
            isPlayingExpression = false;
        }
        
        private BlendShapePreset GetBlendShapePreset(string presetName)
        {
            switch (presetName)
            {
                case "Joy": return BlendShapePreset.Joy;
                case "Angry": return BlendShapePreset.Angry;
                case "Sorrow": return BlendShapePreset.Sorrow;
                case "Fun": return BlendShapePreset.Fun;
                case "Surprised": return BlendShapePreset.Surprised;
                case "Neutral": return BlendShapePreset.Neutral;
                default: return BlendShapePreset.Neutral;
            }
        }
        
        /// <summary>
        /// Get current expression
        /// </summary>
        public string GetCurrentExpression()
        {
            return currentExpression;
        }
        
        /// <summary>
        /// Check if currently playing an expression
        /// </summary>
        public bool IsPlayingExpression()
        {
            return isPlayingExpression;
        }
        
        /// <summary>
        /// Get number of queued expressions
        /// </summary>
        public int GetQueueCount()
        {
            return expressionQueue.Count;
        }
    }
}
