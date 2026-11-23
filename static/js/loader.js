/**
 * CURYENT Page Loader
 * Shows a branded loading screen before page content appears
 */

(function() {
    'use strict';

    // Loading messages that rotate
    const loadingMessages = [
        'Preparing your experience',
        'Loading CURYENT',
        'Connecting to services',
        'Getting everything ready',
        'Almost there'
    ];

    let messageIndex = 0;
    let messageInterval = null;
    let progressInterval = null;
    let progressValue = 0;

    // Create and inject the loader HTML
    function createLoader() {
        // Check if loader already exists
        if (document.getElementById('curyent-loader')) {
            return;
        }

        // Create loader container
        const loader = document.createElement('div');
        loader.id = 'curyent-loader';

        // Floating music notes
        const notes = document.createElement('div');
        notes.className = 'loader-notes';
        notes.innerHTML = `
            <span class="loader-note">♪</span>
            <span class="loader-note">♫</span>
            <span class="loader-note">♬</span>
            <span class="loader-note">♩</span>
            <span class="loader-note">♪</span>
            <span class="loader-note">♫</span>
            <span class="loader-note">♬</span>
            <span class="loader-note">♩</span>
        `;
        loader.appendChild(notes);

        // Logo container
        const logoContainer = document.createElement('div');
        logoContainer.className = 'loader-logo-container';

        // Spinning ring
        const ring = document.createElement('div');
        ring.className = 'loader-ring';

        // Logo image
        const logo = document.createElement('img');
        logo.src = '/logo.png';
        logo.alt = 'CURYENT';
        logo.className = 'loader-logo';
        logo.onerror = function() {
            // Fallback: show icon instead of image
            this.style.display = 'none';
            const fallback = document.createElement('div');
            fallback.style.cssText = 'width:80px;height:80px;display:flex;align-items:center;justify-content:center;font-size:40px;color:#c9a0ff;';
            fallback.innerHTML = '<i class="fas fa-music"></i>';
            ring.appendChild(fallback);
        };

        ring.appendChild(logo);
        logoContainer.appendChild(ring);

        // Brand name
        const brand = document.createElement('div');
        brand.className = 'loader-brand';
        brand.textContent = 'CURYENT';
        logoContainer.appendChild(brand);

        // Tagline
        const tagline = document.createElement('div');
        tagline.className = 'loader-tagline';
        tagline.textContent = 'Event Networking';
        logoContainer.appendChild(tagline);

        loader.appendChild(logoContainer);

        // Progress bar
        const progressContainer = document.createElement('div');
        progressContainer.className = 'loader-progress-container';

        const progressTrack = document.createElement('div');
        progressTrack.className = 'loader-progress-track';

        const progressFill = document.createElement('div');
        progressFill.className = 'loader-progress-fill';
        progressFill.id = 'curyent-progress-fill';
        progressTrack.appendChild(progressFill);

        const progressText = document.createElement('div');
        progressText.className = 'loader-text';
        progressText.id = 'curyent-loader-text';
        progressText.textContent = loadingMessages[0];

        progressContainer.appendChild(progressTrack);
        progressContainer.appendChild(progressText);
        loader.appendChild(progressContainer);

        // Insert at the beginning of body
        document.body.insertBefore(loader, document.body.firstChild);

        // Start progress animation
        startProgress();

        // Start rotating messages
        startMessages();
    }

    // Animate progress bar
    function startProgress() {
        const progressFill = document.getElementById('curyent-progress-fill');
        
        progressInterval = setInterval(function() {
            // Random increment for realistic feel
            const increment = Math.random() * 15 + 5;
            progressValue = Math.min(progressValue + increment, 90); // Cap at 90% until page is ready
            if (progressFill) {
                progressFill.style.width = progressValue + '%';
            }
        }, 200);
    }

    // Rotate loading messages
    function startMessages() {
        const loaderText = document.getElementById('curyent-loader-text');
        
        messageInterval = setInterval(function() {
            messageIndex = (messageIndex + 1) % loadingMessages.length;
            if (loaderText) {
                loaderText.style.opacity = '0';
                setTimeout(function() {
                    loaderText.textContent = loadingMessages[messageIndex];
                    loaderText.style.opacity = '1';
                }, 300);
            }
        }, 2000);
    }

    // Hide the loader
    function hideLoader() {
        const loader = document.getElementById('curyent-loader');
        const progressFill = document.getElementById('curyent-progress-fill');

        // Clear intervals
        if (messageInterval) clearInterval(messageInterval);
        if (progressInterval) clearInterval(progressInterval);

        // Complete progress bar
        if (progressFill) {
            progressFill.style.width = '100%';
        }

        // Update text
        const loaderText = document.getElementById('curyent-loader-text');
        if (loaderText) {
            loaderText.textContent = 'Welcome to CURYENT';
        }

        // Small delay to show 100% progress, then fade out
        setTimeout(function() {
            if (loader) {
                loader.classList.add('hidden');
                
                // Remove from DOM after transition
                setTimeout(function() {
                    if (loader && loader.parentNode) {
                        loader.parentNode.removeChild(loader);
                    }
                }, 600);
            }
        }, 400);
    }

    // Initialize loader immediately
    createLoader();

    // Hide loader when page is fully loaded
    window.addEventListener('load', function() {
        // Small delay to ensure everything is rendered
        setTimeout(hideLoader, 300);
    });

    // Fallback: hide loader after max time (5 seconds)
    setTimeout(function() {
        const loader = document.getElementById('curyent-loader');
        if (loader && !loader.classList.contains('hidden')) {
            hideLoader();
        }
    }, 5000);

    // Expose hide function globally for manual control if needed
    window.hideCuryentLoader = hideLoader;

})();
