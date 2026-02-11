using System.Collections;
using UnityEngine;

namespace Lucy
{
    /// <summary>
    /// Controls idle animations for the VRM avatar
    /// </summary>
    public class IdleAnimationController : MonoBehaviour
    {
        [Header("Animation Settings")]
        [SerializeField] private float blinkInterval = 3.5f;
        [SerializeField] private float blinkVariation = 2.0f;
        [SerializeField] private float blinkDuration = 0.15f;
        
        [Header("Breathing")]
        [SerializeField] private bool enableBreathing = true;
        [SerializeField] private Transform chestBone;
        [SerializeField] private float breathingSpeed = 1.0f;
        [SerializeField] private float breathingIntensity = 0.02f;
        
        [Header("Head Movement")]
        [SerializeField] private bool enableHeadMovement = true;
        [SerializeField] private Transform headBone;
        [SerializeField] private float headMovementSpeed = 0.5f;
        [SerializeField] private float headMovementRange = 10f;
        
        private VRM.VRMBlendShapeProxy blendShapeProxy;
        private float nextBlinkTime;
        private Vector3 chestInitialScale;
        private Quaternion headInitialRotation;
        private Vector3 headTargetRotation;
        private float headMovementTimer;
        
        void Start()
        {
            blendShapeProxy = GetComponentInChildren<VRM.VRMBlendShapeProxy>();
            
            if (blendShapeProxy == null)
            {
                Debug.LogWarning("VRMBlendShapeProxy not found for idle animations");
            }
            
            // Store initial transforms
            if (chestBone != null)
            {
                chestInitialScale = chestBone.localScale;
            }
            
            if (headBone != null)
            {
                headInitialRotation = headBone.localRotation;
                headTargetRotation = Vector3.zero;
            }
            
            // Schedule first blink
            ScheduleNextBlink();
        }
        
        void Update()
        {
            HandleBlinking();
            HandleBreathing();
            HandleHeadMovement();
        }
        
        private void HandleBlinking()
        {
            if (blendShapeProxy == null) return;
            
            if (Time.time >= nextBlinkTime)
            {
                StartCoroutine(Blink());
                ScheduleNextBlink();
            }
        }
        
        private IEnumerator Blink()
        {
            if (blendShapeProxy == null) yield break;
            
            // Close eyes
            float elapsed = 0f;
            while (elapsed < blinkDuration / 2)
            {
                elapsed += Time.deltaTime;
                float value = Mathf.Lerp(0f, 1f, elapsed / (blinkDuration / 2));
                blendShapeProxy.ImmediatelySetValue(VRM.BlendShapePreset.Blink, value);
                yield return null;
            }
            
            // Open eyes
            elapsed = 0f;
            while (elapsed < blinkDuration / 2)
            {
                elapsed += Time.deltaTime;
                float value = Mathf.Lerp(1f, 0f, elapsed / (blinkDuration / 2));
                blendShapeProxy.ImmediatelySetValue(VRM.BlendShapePreset.Blink, value);
                yield return null;
            }
            
            blendShapeProxy.ImmediatelySetValue(VRM.BlendShapePreset.Blink, 0f);
        }
        
        private void ScheduleNextBlink()
        {
            float variation = Random.Range(-blinkVariation, blinkVariation);
            nextBlinkTime = Time.time + blinkInterval + variation;
        }
        
        private void HandleBreathing()
        {
            if (!enableBreathing || chestBone == null) return;
            
            // Subtle breathing animation using sine wave
            float breathCycle = Mathf.Sin(Time.time * breathingSpeed) * breathingIntensity;
            Vector3 breathScale = chestInitialScale + new Vector3(0, breathCycle, breathCycle);
            chestBone.localScale = Vector3.Lerp(chestBone.localScale, breathScale, Time.deltaTime * 2f);
        }
        
        private void HandleHeadMovement()
        {
            if (!enableHeadMovement || headBone == null) return;
            
            headMovementTimer += Time.deltaTime * headMovementSpeed;
            
            // Change head target occasionally
            if (headMovementTimer >= 5f)
            {
                headMovementTimer = 0f;
                headTargetRotation = new Vector3(
                    Random.Range(-headMovementRange, headMovementRange),
                    Random.Range(-headMovementRange, headMovementRange),
                    0f
                );
            }
            
            // Smoothly rotate head towards target
            Quaternion targetRotation = headInitialRotation * Quaternion.Euler(headTargetRotation);
            headBone.localRotation = Quaternion.Slerp(
                headBone.localRotation,
                targetRotation,
                Time.deltaTime * 0.5f
            );
        }
        
        /// <summary>
        /// Enable/disable idle animations
        /// </summary>
        public void SetIdleAnimationsEnabled(bool enabled)
        {
            enableBreathing = enabled;
            enableHeadMovement = enabled;
            this.enabled = enabled;
        }
        
        /// <summary>
        /// Reset to default pose
        /// </summary>
        public void ResetToDefaultPose()
        {
            if (chestBone != null)
            {
                chestBone.localScale = chestInitialScale;
            }
            
            if (headBone != null)
            {
                headBone.localRotation = headInitialRotation;
            }
        }
    }
}
