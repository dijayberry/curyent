// Toggle function to close all dropdowns
function closeAllDropdowns() {
    var navDropdown = document.querySelector('.nav-dropdown');
    var homeDropdown = document.querySelector('.home-dropdown');
    if (navDropdown) navDropdown.classList.remove('open');
    if (homeDropdown) homeDropdown.classList.remove('open');
}

// Nav button toggle (click to open/close, works with hover)
document.querySelector('.nav-btn > button').addEventListener('click', function (e) {
    e.preventDefault();
    e.stopPropagation();
    var navDropdown = document.querySelector('.nav-dropdown');
    var isOpen = navDropdown.classList.contains('open');
    closeAllDropdowns();
    if (!isOpen) {
        navDropdown.classList.add('open');
    }
});

// Home button toggle (click to pin open on small screens only)
document.querySelector('.home-btn > a').addEventListener('click', function (e) {
    e.preventDefault();
    e.stopPropagation();
    if (window.innerWidth > 600) return;
    var homeDropdown = document.querySelector('.home-dropdown');
    var isOpen = homeDropdown.classList.contains('open');
    closeAllDropdowns();
    if (!isOpen) {
        homeDropdown.classList.add('open');
    }
});

// Close dropdown when clicking outside
document.addEventListener('click', function (e) {
    var navBtn = document.querySelector('.nav-btn');
    var homeBtn = document.querySelector('.home-btn');
    var searchBar = document.querySelector('.search-bar');
    if (!navBtn.contains(e.target) && !homeBtn.contains(e.target)) {
        closeAllDropdowns();
    }
    // Close search results when clicking outside search bar
    var searchResults = document.getElementById('search-results');
    if (searchBar && !searchBar.contains(e.target)) {
        searchResults.classList.remove('active');
    }
});

// =========================
// Search Functionality
// =========================

(function () {
    var searchInput = document.getElementById('search-input');
    var searchResults = document.getElementById('search-results');
    var searchBtn = document.getElementById('search-btn');
    var searchTimeout = null;

    if (!searchInput || !searchResults) return;

    function performSearch(query) {
        if (!query || query.length < 1) {
            searchResults.classList.remove('active');
            return;
        }

        fetch('/api/search?q=' + encodeURIComponent(query))
            .then(function (res) { return res.json(); })
            .then(function (data) {
                if (!data.success || !data.users || data.users.length === 0) {
                    searchResults.innerHTML = '<div class="search-empty">No users found</div>';
                    searchResults.classList.add('active');
                    return;
                }

                var html = '';
                data.users.forEach(function (user) {
                    var details = (user.location ? user.location + ' • ' : '') + (user.title || user.role || '');
                    html += '<a href="/bookings?provider_id=' + user.id + '" class="search-result-item">';
                    if (user.profile_image) {
                        html += '<img src="' + user.profile_image + '" alt="' + user.username + '">';
                    } else {
                        html += '<div class="no-image"><i class="fas fa-user"></i></div>';
                    }
                    html += '<div class="search-result-info">';
                    html += '<div class="search-result-name">' + user.username + '</div>';
                    html += '<div class="search-result-details">' + details + '</div>';
                    html += '</div>';
                    html += '<span class="search-result-role">' + (user.role || '') + '</span>';
                    html += '</a>';
                });

                searchResults.innerHTML = html;
                searchResults.classList.add('active');
            })
            .catch(function (err) {
                console.error('Search error:', err);
            });
    }

    // Live search on input with debounce
    searchInput.addEventListener('input', function () {
        var query = this.value.trim();
        if (searchTimeout) clearTimeout(searchTimeout);
        if (query.length >= 1) {
            searchTimeout = setTimeout(function () {
                performSearch(query);
            }, 300);
        } else {
            searchResults.classList.remove('active');
        }
    });

    // Search on button click
    if (searchBtn) {
        searchBtn.addEventListener('click', function () {
            var query = searchInput.value.trim();
            if (query) {
                performSearch(query);
            }
        });
    }

    // Search on Enter key
    searchInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
            var query = this.value.trim();
            if (query) {
                performSearch(query);
            }
        }
    });
})();

// Role selection popup
var rolePopup = document.getElementById('role');
var roleCloseBtn = document.getElementById('role-close');
var roleOverlay = document.querySelector('.role-overlay');

// Open role popup when Account link is clicked
document.querySelectorAll('a[href="#account"]').forEach(function (link) {
    link.addEventListener('click', function (e) {
        e.preventDefault();
        rolePopup.classList.add('active');
    });
});

// Also handle the nav-links Account link
document.querySelectorAll('.nav-links a').forEach(function (link) {
    if (link.getAttribute('href') === '/account') {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            rolePopup.classList.add('active');
        });
    }
});

// Close role popup and go back to home
if (roleCloseBtn) {
    roleCloseBtn.addEventListener('click', function () {
        window.location.href = '/';
    });
}

// Close role popup when clicking overlay background and go back to home
if (roleOverlay) {
    roleOverlay.addEventListener('click', function (e) {
        if (e.target === roleOverlay) {
            window.location.href = '/';
        }
    });
}

// =========================
// Badge Helper — Update Badge Display
// =========================

function updateBadgeDisplay(badges, count) {
    badges.forEach(function (badge) {
        if (!badge) return;
        if (count > 0) {
            badge.textContent = count > 99 ? '99+' : count;
            badge.style.display = 'inline-block';
        } else {
            badge.style.display = 'none';
        }
    });
}

// =========================
// Chat Badge — Unread Message Count
// =========================

(function () {
    var isLoggedIn = window.__homeLoggedIn === true;
    if (!isLoggedIn) return;

    var chatBadgeDesktop = document.getElementById('chat-badge-desktop');
    var chatBadgeMobile = document.getElementById('chat-badge-mobile');
    var chatBadges = [chatBadgeDesktop, chatBadgeMobile];

    function fetchChatUnreadCount() {
        fetch('/api/chat/unread-total')
            .then(function (res) { return res.json(); })
            .catch(function () { return { success: false }; })
            .then(function (result) {
                var count = result.success ? result.unread_total || 0 : 0;
                updateBadgeDisplay(chatBadges, count);
            });
    }

    // Initial fetch
    fetchChatUnreadCount();

    // Poll every 5 seconds
    setInterval(fetchChatUnreadCount, 5000);
})();

// =========================
// Notification Badge — Unread Notification Count
// =========================

(function () {
    var isLoggedIn = window.__homeLoggedIn === true;
    if (!isLoggedIn) return;

    var notifBadgeDesktop = document.getElementById('notif-badge-desktop');
    var notifBadgeMobile = document.getElementById('notif-badge-mobile');
    var notifBadges = [notifBadgeDesktop, notifBadgeMobile];

    function fetchNotifUnreadCount() {
        fetch('/api/notifications/unread-count')
            .then(function (res) { return res.json(); })
            .catch(function () { return { success: false }; })
            .then(function (result) {
                var count = result.success ? result.unread_count || 0 : 0;
                updateBadgeDisplay(notifBadges, count);
            });
    }

    // Initial fetch
    fetchNotifUnreadCount();

    // Poll every 5 seconds
    setInterval(fetchNotifUnreadCount, 5000);
})();

// =========================
// Role Sections — Slideshow Carousel
// =========================

(function () {
    var roleSections = [
        { role: 'dj', slideshowId: 'dj-slideshow', dropdownId: 'dj-dropdown', label: 'DJs', icon: 'fa-music' },
        { role: 'event', slideshowId: 'events-slideshow', dropdownId: 'events-dropdown', label: 'Events', icon: 'fa-calendar-days' },
        { role: 'photographer', slideshowId: 'photographers-slideshow', dropdownId: 'photographers-dropdown', label: 'Photographers', icon: 'fa-camera' },
        { role: 'tents', slideshowId: 'tents-slideshow', dropdownId: 'tents-dropdown', label: 'Tents', icon: 'fa-campground' },
        { role: 'caterer', slideshowId: 'caterer-slideshow', dropdownId: 'caterer-dropdown', label: 'Caterers', icon: 'fa-utensils' }
    ];

    // Cards per slide based on viewport
    function getCardsPerView() {
        var w = window.innerWidth;
        if (w <= 480) return 1;
        if (w <= 768) return 1;
        if (w <= 1024) return 3;
        return 4;
    }

    function formatPrice(price, role) {
        if (price == null || price === undefined) return 'Contact for price';
        var num = parseFloat(price);
        if (isNaN(num)) return 'Contact for price';
        if (role === 'caterer') {
            return '$' + num.toFixed(2) + '/person';
        }
        return '$' + num.toFixed(2) + '/event';
    }

    function createProfileCard(user, role) {
        var card = document.createElement('a');
        card.className = 'profile-card';
        card.href = '/bookings?provider_id=' + user.id;

        var bg = document.createElement('div');
        bg.className = 'profile-card-bg';
        if (user.profile_image) {
            bg.style.backgroundImage = 'url("' + user.profile_image + '")';
        }

        var overlay = document.createElement('div');
        overlay.className = 'profile-card-overlay';

        var content = document.createElement('div');
        content.className = 'profile-card-content';

        var username = document.createElement('div');
        username.className = 'profile-card-username';
        username.textContent = user.username;
        username.title = user.username;

        var location = document.createElement('div');
        location.className = 'profile-card-location';
        var locIcon = document.createElement('i');
        locIcon.className = 'fas fa-map-marker-alt';
        location.appendChild(locIcon);
        if (user.location) {
            location.appendChild(document.createTextNode(user.location));
        } else {
            location.appendChild(document.createTextNode('Location not set'));
        }

        var price = document.createElement('div');
        price.className = 'profile-card-price';
        price.textContent = formatPrice(user.price, role);

        content.appendChild(username);
        content.appendChild(location);
        content.appendChild(price);

        card.appendChild(bg);
        card.appendChild(overlay);
        card.appendChild(content);

        return card;
    }

    function createEmptyState(label, icon) {
        var div = document.createElement('div');
        div.className = 'empty-state';

        var iconEl = document.createElement('i');
        iconEl.className = 'fas ' + icon;

        var p = document.createElement('p');
        p.textContent = 'No ' + label + ' available yet';

        var span = document.createElement('span');
        span.textContent = 'Be the first to sign up!';

        div.appendChild(iconEl);
        div.appendChild(p);
        div.appendChild(span);

        return div;
    }

    // Slideshow state per section
    var slideshowStates = {};

    function initSlideshow(section, users) {
        var container = document.getElementById(section.slideshowId);
        if (!container) return;

        var track = container.querySelector('.slide-track');
        var dotsContainer = container.querySelector('.slide-dots');
        var prevBtn = container.querySelector('.slide-prev');
        var nextBtn = container.querySelector('.slide-next');
        var dropdown = document.getElementById(section.dropdownId);
        var viewAllBtn = container.closest('.role-section').querySelector('.view-all-btn');

        if (!track || !dotsContainer || !prevBtn || !nextBtn) return;

        var cardsPerView = getCardsPerView();
        var totalSlides = Math.ceil(users.length / cardsPerView);

        if (totalSlides <= 1) {
            // Not enough for slideshow — show all in track, hide arrows and dots
            track.innerHTML = '';
            users.forEach(function (user) {
                track.appendChild(createProfileCard(user, section.role));
            });
            prevBtn.style.display = 'none';
            nextBtn.style.display = 'none';
            dotsContainer.style.display = 'none';

            // Still populate dropdown
            if (dropdown) {
                var grid = dropdown.querySelector('.profile-grid');
                if (grid) {
                    users.forEach(function (user) {
                        grid.appendChild(createProfileCard(user, section.role));
                    });
                }
            }
            return;
        }

        // Store state
        slideshowStates[section.slideshowId] = {
            currentSlide: 0,
            currentCard: 0,
            totalSlides: totalSlides,
            cardsPerView: cardsPerView,
            users: users,
            autoPlayTimer: null,
            section: section
        };

        // Build slides
        track.innerHTML = '';
        for (var i = 0; i < users.length; i++) {
            track.appendChild(createProfileCard(users[i], section.role));
        }

        // Build dots
        dotsContainer.innerHTML = '';
        for (var d = 0; d < totalSlides; d++) {
            (function (idx) {
                var dot = document.createElement('button');
                dot.className = 'slide-dot' + (idx === 0 ? ' active' : '');
                dot.setAttribute('aria-label', 'Go to slide ' + (idx + 1));
                dot.addEventListener('click', function () {
                    goToSlide(section.slideshowId, idx);
                    resetAutoPlay(section.slideshowId);
                });
                dotsContainer.appendChild(dot);
            })(d);
        }

        // Arrow events — one card at a time
        prevBtn.addEventListener('click', function () {
            var state = slideshowStates[section.slideshowId];
            if (!state) return;
            // Only slide left on explicit user click
            if (state.currentCard > 0) {
                state.currentCard--;
                goToSlideByCard(section.slideshowId, state.currentCard);
            }
            resetAutoPlay(section.slideshowId);
        });

        nextBtn.addEventListener('click', function () {
            var state = slideshowStates[section.slideshowId];
            if (!state) return;
            var cardElements = container.querySelectorAll('.profile-card');
            var totalCards = cardElements.length;
            var maxCard = totalCards - state.cardsPerView;
            if (maxCard < 0) maxCard = 0;
            if (state.currentCard < maxCard) {
                state.currentCard++;
                goToSlideByCard(section.slideshowId, state.currentCard);
            }
            resetAutoPlay(section.slideshowId);
        });

        // Pause on hover
        container.addEventListener('mouseenter', function () {
            stopAutoPlay(section.slideshowId);
        });

        container.addEventListener('mouseleave', function () {
            startAutoPlay(section.slideshowId);
        });

        // View All button — popup toggle
        if (viewAllBtn && dropdown) {
            // Populate dropdown grid
            var grid = dropdown.querySelector('.profile-grid');
            if (grid) {
                users.forEach(function (user) {
                    grid.appendChild(createProfileCard(user, section.role));
                });
            }

            viewAllBtn.addEventListener('click', function (e) {
                e.stopPropagation();
                var isOpen = dropdown.classList.contains('open');

                // Close all other dropdowns first
                var allDropdowns = document.querySelectorAll('.all-users-dropdown');
                var allBtns = document.querySelectorAll('.view-all-btn');
                allDropdowns.forEach(function (dd) {
                    dd.classList.remove('open');
                });
                allBtns.forEach(function (btn) {
                    btn.classList.remove('active');
                    btn.innerHTML = '<i class="fas fa-th"></i> View All';
                });

                // Toggle current dropdown
                if (!isOpen) {
                    dropdown.classList.add('open');
                    viewAllBtn.classList.add('active');
                    viewAllBtn.innerHTML = '<i class="fas fa-chevron-up"></i> Show Less';
                }
            });
        }

        // Start auto-play immediately
        startAutoPlay(section.slideshowId);
    }

    function goToSlide(slideshowId, slideIndex) {
        var state = slideshowStates[slideshowId];
        if (!state) return;

        state.currentSlide = slideIndex;
        state.currentCard = slideIndex * state.cardsPerView;
        var container = document.getElementById(slideshowId);
        var track = container.querySelector('.slide-track');
        var dotsContainer = container.querySelector('.slide-dots');
        var prevBtn = container.querySelector('.slide-prev');
        var nextBtn = container.querySelector('.slide-next');

        var cardElements = track.querySelectorAll('.profile-card');
        if (cardElements.length === 0) return;

        // Calculate card width including gap
        var firstCard = cardElements[0];
        var cardWidth = firstCard.offsetWidth;
        var trackStyle = window.getComputedStyle(track);
        var gap = parseFloat(trackStyle.gap) || 20;
        var offset = state.currentCard * (cardWidth + gap);

        track.style.transform = 'translateX(-' + offset + 'px)';

        // Update dots
        var dots = dotsContainer.querySelectorAll('.slide-dot');
        dots.forEach(function (dot, idx) {
            dot.classList.toggle('active', idx === slideIndex);
        });

        // Highlight active center card on mobile
        cardElements.forEach(function (card, idx) {
            card.classList.toggle('active', idx === state.currentCard);
        });

        // Update arrow disabled state
        var totalCards = cardElements.length;
        var maxCard = totalCards - state.cardsPerView;
        if (maxCard < 0) maxCard = 0;
        prevBtn.disabled = state.currentCard <= 0;
        nextBtn.disabled = state.currentCard >= maxCard;
    }

    // Navigate by single card position (one-by-one sliding)
    function goToSlideByCard(slideshowId, cardIndex) {
        var state = slideshowStates[slideshowId];
        if (!state) return;

        state.currentCard = cardIndex;
        state.currentSlide = Math.floor(cardIndex / state.cardsPerView);
        var container = document.getElementById(slideshowId);
        var track = container.querySelector('.slide-track');
        var dotsContainer = container.querySelector('.slide-dots');
        var prevBtn = container.querySelector('.slide-prev');
        var nextBtn = container.querySelector('.slide-next');

        var cardElements = track.querySelectorAll('.profile-card');
        if (cardElements.length === 0) return;

        var firstCard = cardElements[0];
        var cardWidth = firstCard.offsetWidth;
        var trackStyle2 = window.getComputedStyle(track);
        var gap2 = parseFloat(trackStyle2.gap) || 20;
        var offset = cardIndex * (cardWidth + gap2);

        track.style.transform = 'translateX(-' + offset + 'px)';

        // Update dots based on current slide
        var dots = dotsContainer.querySelectorAll('.slide-dot');
        dots.forEach(function (dot, idx) {
            dot.classList.toggle('active', idx === state.currentSlide);
        });

        // Highlight active center card on mobile
        cardElements.forEach(function (card, idx) {
            card.classList.toggle('active', idx === cardIndex);
        });

        // Update arrow disabled state
        var totalCards = cardElements.length;
        var maxCard = totalCards - state.cardsPerView;
        if (maxCard < 0) maxCard = 0;
        prevBtn.disabled = cardIndex <= 0;
        nextBtn.disabled = cardIndex >= maxCard;
    }

    function startAutoPlay(slideshowId) {
        var state = slideshowStates[slideshowId];
        if (!state || state.totalSlides <= 1) return;
        stopAutoPlay(slideshowId);
        state.autoPlayTimer = setInterval(function () {
            // Slide one card at a time to the right
            var container = document.getElementById(slideshowId);
            var cardElements = container.querySelectorAll('.profile-card');
            var totalCards = cardElements.length;
            if (totalCards === 0) return;

            var track = container.querySelector('.slide-track');
            var currentCard = state.currentCard || 0;
            var maxCard = totalCards - state.cardsPerView;
            if (maxCard < 0) maxCard = 0;

            if (currentCard < maxCard) {
                // Advance one card to the right
                state.currentCard = currentCard + 1;
                goToSlideByCard(slideshowId, state.currentCard);
            } else {
                // Reached the end — smoothly loop back to the beginning
                // Disable transition, reset to 0, then re-enable and slide to next card
                track.style.transition = 'none';
                state.currentCard = 0;
                goToSlideByCard(slideshowId, 0);

                // Force browser to apply the instant reset before re-enabling transition
                track.offsetHeight; // trigger reflow

                // Re-enable transition and slide to the next card
                track.style.transition = '';
                state.currentCard = 1;
                goToSlideByCard(slideshowId, 1);
            }
        }, 4000);
    }

    function stopAutoPlay(slideshowId) {
        var state = slideshowStates[slideshowId];
        if (state && state.autoPlayTimer) {
            clearInterval(state.autoPlayTimer);
            state.autoPlayTimer = null;
        }
    }

    function resetAutoPlay(slideshowId) {
        stopAutoPlay(slideshowId);
        startAutoPlay(slideshowId);
    }

    // Handle resize: recalculate slides
    var resizeTimer;
    window.addEventListener('resize', function () {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function () {
            // Reinitialize all slideshows that have state
            for (var id in slideshowStates) {
                var state = slideshowStates[id];
                if (!state) continue;
                var newCardsPerView = getCardsPerView();
                if (newCardsPerView !== state.cardsPerView) {
                    // Save current card position before rebuild
                    var savedCard = state.currentCard || 0;
                    stopAutoPlay(id);
                    initSlideshow(state.section, state.users);
                    // Restore card position after rebuild
                    if (slideshowStates[id]) {
                        slideshowStates[id].currentCard = savedCard;
                        goToSlideByCard(id, savedCard);
                    }
                } else {
                    // Just reposition using current card
                    goToSlideByCard(id, state.currentCard || 0);
                }
            }
        }, 200);
    });

    function loadRoleUsers(section) {
        var container = document.getElementById(section.slideshowId);
        if (!container) return;

        fetch('/api/users-by-role?role=' + section.role)
            .then(function (res) { return res.json(); })
            .then(function (result) {
                if (!result.success || !result.users || result.users.length === 0) {
                    var track = container.querySelector('.slide-track');
                    var prevBtn = container.querySelector('.slide-prev');
                    var nextBtn = container.querySelector('.slide-next');
                    var dotsContainer = container.querySelector('.slide-dots');
                    if (track) track.innerHTML = '';
                    if (track) track.appendChild(createEmptyState(section.label, section.icon));
                    if (prevBtn) prevBtn.style.display = 'none';
                    if (nextBtn) nextBtn.style.display = 'none';
                    if (dotsContainer) dotsContainer.style.display = 'none';
                    return;
                }

                initSlideshow(section, result.users);
            })
            .catch(function () {
                var track = container.querySelector('.slide-track');
                if (track) {
                    track.innerHTML = '';
                    var div = document.createElement('div');
                    div.className = 'empty-state';
                    var p = document.createElement('p');
                    p.textContent = 'Failed to load ' + section.label;
                    div.appendChild(p);
                    track.appendChild(div);
                }
            });
    }

    // Load all role sections
    roleSections.forEach(function (section) {
        loadRoleUsers(section);
    });

    // Intersection Observer: start auto-play only when a slideshow scrolls into view
    if ('IntersectionObserver' in window) {
        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                var slideshowId = entry.target.getAttribute('data-slideshow-id');
                if (entry.isIntersecting) {
                    // Section is visible — start auto-play
                    startAutoPlay(slideshowId);
                } else {
                    // Section left the viewport — stop auto-play to save resources
                    stopAutoPlay(slideshowId);
                }
            });
        }, { threshold: 0.1 });

        // Observe each slideshow container
        roleSections.forEach(function (section) {
            var container = document.getElementById(section.slideshowId);
            if (container) {
                container.setAttribute('data-slideshow-id', section.slideshowId);
                observer.observe(container);
            }
        });
    }

    // Close button handler: close dropdown when X is clicked
    document.addEventListener('click', function (e) {
        var closeBtn = e.target.closest('.dropdown-close');
        if (closeBtn) {
            var dropdown = closeBtn.closest('.all-users-dropdown');
            if (dropdown) {
                dropdown.classList.remove('open');
                var btn = dropdown.closest('.view-all-wrapper').querySelector('.view-all-btn');
                if (btn) {
                    btn.classList.remove('active');
                    btn.innerHTML = '<i class="fas fa-th"></i> View All';
                }
            }
            return;
        }
    });

    // Global click handler: close all dropdowns when clicking outside
    document.addEventListener('click', function (e) {
        var allDropdowns = document.querySelectorAll('.all-users-dropdown');
        var allBtns = document.querySelectorAll('.view-all-btn');
        var allWrappers = document.querySelectorAll('.view-all-wrapper');

        // Check if click is directly on a dropdown overlay (not on content inside it)
        allDropdowns.forEach(function (dd) {
            if (dd.contains(e.target) && e.target !== dd.querySelector('.profile-grid') && !dd.querySelector('.profile-grid').contains(e.target)) {
                dd.classList.remove('open');
                var btn = dd.closest('.view-all-wrapper').querySelector('.view-all-btn');
                if (btn) {
                    btn.classList.remove('active');
                    btn.innerHTML = '<i class="fas fa-th"></i> View All';
                }
                return;
            }
        });

        // Check if click is inside any view-all-wrapper (but not on dropdown overlay)
        var insideWrapper = false;
        allWrappers.forEach(function (wrapper) {
            if (wrapper.contains(e.target)) {
                insideWrapper = true;
            }
        });

        if (!insideWrapper) {
            // Close all dropdowns
            allDropdowns.forEach(function (dd) {
                dd.classList.remove('open');
            });
            allBtns.forEach(function (btn) {
                btn.classList.remove('active');
                btn.innerHTML = '<i class="fas fa-th"></i> View All';
            });
        }
    });
})();
