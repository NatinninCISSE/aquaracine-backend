/**
 * Aqua-Racine API Integration
 * Gestion des appels API vers le backend Django
 */

const AquaRacineAPI = (function() {
    'use strict';

    // Configuration API
    const CONFIG = {
        baseURL: 'http://localhost:8000/api',
        timeout: 30000
    };

    // Utilitaires
    const utils = {
        // Faire un appel API
        async fetch(endpoint, options = {}) {
            const url = `${CONFIG.baseURL}${endpoint}`;
            const defaultOptions = {
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            };

            try {
                const response = await fetch(url, { ...defaultOptions, ...options });
                const data = await response.json();

                if (!response.ok) {
                    throw { status: response.status, data };
                }

                return { success: true, data };
            } catch (error) {
                console.error('API Error:', error);
                return { success: false, error };
            }
        },

        // GET request
        async get(endpoint) {
            return this.fetch(endpoint, { method: 'GET' });
        },

        // POST request
        async post(endpoint, data) {
            return this.fetch(endpoint, {
                method: 'POST',
                body: JSON.stringify(data)
            });
        },

        // POST avec FormData (pour fichiers)
        async postFormData(endpoint, formData) {
            const url = `${CONFIG.baseURL}${endpoint}`;
            try {
                const response = await fetch(url, {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();

                if (!response.ok) {
                    throw { status: response.status, data };
                }

                return { success: true, data };
            } catch (error) {
                console.error('API Error:', error);
                return { success: false, error };
            }
        }
    };

    // API publique
    return {
        // Configuration
        setBaseURL(url) {
            CONFIG.baseURL = url;
        },

        // ========================================
        // DONNÉES DU SITE
        // ========================================

        // Récupérer toutes les données du site en une requête
        async getFullSiteData() {
            return utils.get('/site-data/');
        },

        // Récupérer les paramètres du site
        async getSettings() {
            return utils.get('/settings/');
        },

        // ========================================
        // HERO SLIDES
        // ========================================
        async getHeroSlides() {
            return utils.get('/hero-slides/');
        },

        // ========================================
        // SERVICES
        // ========================================
        async getServices() {
            return utils.get('/services/');
        },

        // ========================================
        // PRODUITS
        // ========================================
        async getProducts(params = {}) {
            const queryString = new URLSearchParams(params).toString();
            return utils.get(`/products/${queryString ? '?' + queryString : ''}`);
        },

        async getProductBySlug(slug) {
            return utils.get(`/products/${slug}/`);
        },

        async getFeaturedProducts() {
            return utils.get('/products/featured/');
        },

        async getProductCategories() {
            return utils.get('/product-categories/');
        },

        // ========================================
        // ÉQUIPE
        // ========================================
        async getTeamMembers() {
            return utils.get('/team-members/');
        },

        // ========================================
        // BLOG
        // ========================================
        async getBlogPosts(params = {}) {
            const queryString = new URLSearchParams(params).toString();
            return utils.get(`/blog-posts/${queryString ? '?' + queryString : ''}`);
        },

        async getBlogPostBySlug(slug) {
            return utils.get(`/blog-posts/${slug}/`);
        },

        async getBlogCategories() {
            return utils.get('/blog-categories/');
        },

        // ========================================
        // TIMELINE / PROCESSUS
        // ========================================
        async getTimelineSteps() {
            return utils.get('/timeline-steps/');
        },

        // ========================================
        // GALERIE
        // ========================================
        async getGalleryImages() {
            return utils.get('/gallery-images/');
        },

        // ========================================
        // AVANTAGES
        // ========================================
        async getAdvantages() {
            return utils.get('/advantages/');
        },

        // ========================================
        // TÉMOIGNAGES
        // ========================================
        async getTestimonials() {
            return utils.get('/testimonials/');
        },

        // ========================================
        // FAQ
        // ========================================
        async getFAQs(category = null) {
            const params = category ? `?category=${category}` : '';
            return utils.get(`/faqs/${params}`);
        },

        // ========================================
        // TYPES D'INSTALLATION (pour devis)
        // ========================================
        async getInstallationTypes() {
            return utils.get('/installation-types/');
        },

        // ========================================
        // DEMANDE DE DEVIS
        // ========================================
        async submitQuoteRequest(data) {
            return utils.post('/quote-request/', data);
        },

        async submitQuoteRequestWithFile(formData) {
            return utils.postFormData('/quote-request/', formData);
        },

        // ========================================
        // CONTACT
        // ========================================
        async submitContactMessage(data) {
            return utils.post('/contact/', data);
        },

        // ========================================
        // NEWSLETTER
        // ========================================
        async subscribeNewsletter(email) {
            return utils.post('/newsletter/', { email });
        }
    };
})();


/**
 * Gestionnaire de formulaires Aqua-Racine
 */
const AquaRacineForms = (function() {
    'use strict';

    // Afficher une notification
    function showNotification(message, type = 'success') {
        // Supprimer les notifications existantes
        const existingNotif = document.querySelector('.ar-notification');
        if (existingNotif) {
            existingNotif.remove();
        }

        const notification = document.createElement('div');
        notification.className = `ar-notification ar-notification-${type}`;
        notification.innerHTML = `
            <div class="ar-notification-content">
                <i class="fa ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
                <span>${message}</span>
                <button class="ar-notification-close">&times;</button>
            </div>
        `;

        document.body.appendChild(notification);

        // Animation d'entrée
        setTimeout(() => notification.classList.add('show'), 10);

        // Fermeture automatique
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 5000);

        // Fermeture manuelle
        notification.querySelector('.ar-notification-close').addEventListener('click', () => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        });
    }

    // Valider un email
    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    // Valider un téléphone
    function isValidPhone(phone) {
        return /^[\d\s\+\-\(\)]{8,20}$/.test(phone);
    }

    // Afficher les erreurs de validation
    function showFieldError(field, message) {
        field.classList.add('error');
        let errorEl = field.parentNode.querySelector('.field-error');
        if (!errorEl) {
            errorEl = document.createElement('span');
            errorEl.className = 'field-error';
            field.parentNode.appendChild(errorEl);
        }
        errorEl.textContent = message;
    }

    // Supprimer les erreurs de validation
    function clearFieldError(field) {
        field.classList.remove('error');
        const errorEl = field.parentNode.querySelector('.field-error');
        if (errorEl) {
            errorEl.remove();
        }
    }

    // Activer/Désactiver le bouton de soumission
    function setSubmitLoading(button, loading) {
        if (loading) {
            button.disabled = true;
            button.dataset.originalText = button.textContent;
            button.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Envoi en cours...';
        } else {
            button.disabled = false;
            button.textContent = button.dataset.originalText || 'Envoyer';
        }
    }

    return {
        // Initialiser le formulaire de demande de devis
        initQuoteForm(formSelector) {
            const form = document.querySelector(formSelector);
            if (!form) return;

            // Charger les types d'installation
            this.loadInstallationTypes();

            form.addEventListener('submit', async (e) => {
                e.preventDefault();

                const submitBtn = form.querySelector('button[type="submit"]');
                let isValid = true;

                // Validation
                const requiredFields = form.querySelectorAll('[required]');
                requiredFields.forEach(field => {
                    clearFieldError(field);
                    if (!field.value.trim()) {
                        showFieldError(field, 'Ce champ est requis');
                        isValid = false;
                    }
                });

                const emailField = form.querySelector('input[type="email"]');
                if (emailField && emailField.value && !isValidEmail(emailField.value)) {
                    showFieldError(emailField, 'Email invalide');
                    isValid = false;
                }

                const phoneField = form.querySelector('input[name="phone"]');
                if (phoneField && phoneField.value && !isValidPhone(phoneField.value)) {
                    showFieldError(phoneField, 'Numéro de téléphone invalide');
                    isValid = false;
                }

                // Vérifier qu'au moins un type d'installation est sélectionné
                const installationTypes = form.querySelectorAll('input[name="installation_types"]:checked');
                if (installationTypes.length === 0) {
                    showNotification('Veuillez sélectionner au moins un type d\'installation', 'error');
                    isValid = false;
                }

                if (!isValid) return;

                setSubmitLoading(submitBtn, true);

                // Préparer les données
                const formData = new FormData(form);
                const data = {
                    first_name: formData.get('first_name'),
                    last_name: formData.get('last_name'),
                    email: formData.get('email'),
                    phone: formData.get('phone'),
                    company: formData.get('company') || '',
                    city: formData.get('city'),
                    address: formData.get('address') || '',
                    installation_types: Array.from(installationTypes).map(cb => parseInt(cb.value)),
                    project_size: formData.get('project_size'),
                    surface_area: formData.get('surface_area') || '',
                    budget_range: formData.get('budget_range') || '',
                    timeline: formData.get('timeline') || '',
                    description: formData.get('description'),
                    has_water_source: formData.get('has_water_source') === 'on',
                    has_electricity: formData.get('has_electricity') === 'on',
                    needs_training: formData.get('needs_training') === 'on',
                    needs_maintenance: formData.get('needs_maintenance') === 'on'
                };

                // Envoyer la demande
                const result = await AquaRacineAPI.submitQuoteRequest(data);

                setSubmitLoading(submitBtn, false);

                if (result.success) {
                    showNotification(result.data.message || 'Votre demande de devis a été envoyée avec succès !', 'success');
                    form.reset();
                    // Scroll vers le haut du formulaire
                    form.scrollIntoView({ behavior: 'smooth', block: 'start' });
                } else {
                    const errorMsg = result.error?.data?.detail || 'Une erreur est survenue. Veuillez réessayer.';
                    showNotification(errorMsg, 'error');
                }
            });
        },

        // Charger les types d'installation dynamiquement
        async loadInstallationTypes() {
            const container = document.querySelector('#installation-types-container');
            if (!container) return;

            const result = await AquaRacineAPI.getInstallationTypes();
            if (result.success && result.data.results) {
                container.innerHTML = result.data.results.map(type => `
                    <div class="installation-type-option">
                        <input type="checkbox" name="installation_types" value="${type.id}" id="inst-${type.id}">
                        <label for="inst-${type.id}">
                            <i class="${type.icon}"></i>
                            <span class="inst-name">${type.name}</span>
                            <span class="inst-desc">${type.description || ''}</span>
                        </label>
                    </div>
                `).join('');
            }
        },

        // Initialiser le formulaire de contact
        initContactForm(formSelector) {
            const form = document.querySelector(formSelector);
            if (!form) return;

            form.addEventListener('submit', async (e) => {
                e.preventDefault();

                const submitBtn = form.querySelector('button[type="submit"]');
                let isValid = true;

                // Validation
                const name = form.querySelector('input[name="name"]');
                const email = form.querySelector('input[name="email"]');
                const message = form.querySelector('textarea[name="message"]');

                [name, email, message].forEach(field => {
                    if (field) clearFieldError(field);
                });

                if (!name?.value.trim()) {
                    showFieldError(name, 'Veuillez entrer votre nom');
                    isValid = false;
                }

                if (!email?.value.trim() || !isValidEmail(email.value)) {
                    showFieldError(email, 'Veuillez entrer un email valide');
                    isValid = false;
                }

                if (!message?.value.trim()) {
                    showFieldError(message, 'Veuillez entrer votre message');
                    isValid = false;
                }

                if (!isValid) return;

                setSubmitLoading(submitBtn, true);

                const data = {
                    name: name.value.trim(),
                    email: email.value.trim(),
                    phone: form.querySelector('input[name="phone"]')?.value || '',
                    subject: form.querySelector('input[name="subject"]')?.value || '',
                    message: message.value.trim()
                };

                const result = await AquaRacineAPI.submitContactMessage(data);

                setSubmitLoading(submitBtn, false);

                if (result.success) {
                    showNotification(result.data.message || 'Votre message a été envoyé avec succès !', 'success');
                    form.reset();
                } else {
                    showNotification('Une erreur est survenue. Veuillez réessayer.', 'error');
                }
            });
        },

        // Initialiser le formulaire newsletter
        initNewsletterForm(formSelector) {
            const form = document.querySelector(formSelector);
            if (!form) return;

            form.addEventListener('submit', async (e) => {
                e.preventDefault();

                const emailInput = form.querySelector('input[type="text"], input[type="email"]');
                const submitBtn = form.querySelector('button[type="submit"]');

                if (!emailInput?.value.trim() || !isValidEmail(emailInput.value)) {
                    showNotification('Veuillez entrer un email valide', 'error');
                    return;
                }

                setSubmitLoading(submitBtn, true);

                const result = await AquaRacineAPI.subscribeNewsletter(emailInput.value.trim());

                setSubmitLoading(submitBtn, false);

                if (result.success) {
                    showNotification(result.data.message || 'Inscription réussie !', 'success');
                    form.reset();
                } else {
                    showNotification('Une erreur est survenue. Veuillez réessayer.', 'error');
                }
            });
        },

        // Initialiser tous les formulaires
        initAll() {
            this.initQuoteForm('#quote-form');
            this.initContactForm('#contact-form');
            this.initNewsletterForm('#newsletter-form');
        },

        // Utilitaires exposés
        showNotification
    };
})();


/**
 * Chargement dynamique du contenu depuis l'API
 */
const AquaRacineContent = (function() {
    'use strict';

    // Cache pour les données
    let siteData = null;

    return {
        // Charger toutes les données du site
        async loadSiteData() {
            if (siteData) return siteData;

            const result = await AquaRacineAPI.getFullSiteData();
            if (result.success) {
                siteData = result.data;
                return siteData;
            }
            return null;
        },

        // Mettre à jour les slides hero
        updateHeroSlides(slides) {
            const container = document.querySelector('.hero-area-slide');
            if (!container || !slides?.length) return;

            container.innerHTML = slides.map(slide => `
                <div class="hero-area-single-slide">
                    <h1>${slide.title}</h1>
                    <p>${slide.description || slide.subtitle}</p>
                    <a href="${slide.button_url}" class="aquaponic-btn">${slide.button_text}</a>
                </div>
            `).join('');

            // Réinitialiser le carousel
            if (typeof $.fn.owlCarousel !== 'undefined') {
                $(container).trigger('destroy.owl.carousel');
                $(container).owlCarousel({
                    items: 1,
                    loop: true,
                    autoplay: true,
                    autoplayTimeout: 5000,
                    nav: false,
                    dots: true
                });
            }
        },

        // Mettre à jour les services
        updateServices(services) {
            const container = document.querySelector('.our-foods .row');
            if (!container || !services?.length) return;

            container.innerHTML = services.map(service => `
                <div class="col-lg-6 col-md-6">
                    <div class="our-foods-list flexbox-center">
                        <div class="our-foods-icon">
                            <i class="${service.icon}"></i>
                        </div>
                        <div class="our-foods-info">
                            <h4>${service.title}</h4>
                            <p>${service.description}</p>
                        </div>
                    </div>
                </div>
            `).join('');
        },

        // Mettre à jour les produits
        updateProducts(products) {
            const container = document.querySelector('.product-gallery .row');
            if (!container || !products?.length) return;

            // Garder le titre
            const titleRow = container.querySelector('.col-lg-12');
            const titleHtml = titleRow ? titleRow.outerHTML : '';

            container.innerHTML = titleHtml + products.map(product => `
                <div class="col-lg-3 col-sm-6">
                    <div class="single-product max-width-320">
                        <div class="single-product-img">
                            <img src="${product.image}" alt="${product.name}">
                            <div class="product-img-overlay">
                                <a href="#" class="aquaponic-btn" data-product-id="${product.id}">
                                    Ajouter au panier <i class="fa fa-shopping-cart"></i>
                                </a>
                            </div>
                        </div>
                        <div class="single-product-info">
                            <p><a href="product-details.html?slug=${product.slug}">${product.name}</a></p>
                            <h4>${product.price.toLocaleString()} FCFA</h4>
                            <a href="product-details.html?slug=${product.slug}" class="buy-product">Voir détails</a>
                        </div>
                    </div>
                </div>
            `).join('');
        },

        // Mettre à jour l'équipe
        updateTeamMembers(members) {
            const container = document.querySelector('.team-member .row .row');
            if (!container || !members?.length) return;

            container.innerHTML = members.map(member => `
                <div class="col-lg-4 col-sm-6">
                    <div class="single-member max-width-320">
                        <div class="single-member-img">
                            <img src="${member.photo}" alt="${member.name}">
                        </div>
                        <div class="single-member-info">
                            <p><a href="#">${member.name}</a></p>
                            <span class="member-role">${member.role}</span>
                            <div class="single-member-contact">
                                ${member.linkedin_url ? `<a href="${member.linkedin_url}" target="_blank"><i class="fa fa-linkedin"></i></a>` : ''}
                                ${member.facebook_url ? `<a href="${member.facebook_url}" target="_blank"><i class="fa fa-facebook"></i></a>` : ''}
                                ${member.twitter_url ? `<a href="${member.twitter_url}" target="_blank"><i class="fa fa-twitter"></i></a>` : ''}
                            </div>
                            <a href="team.html" class="read-more">Voir le profil<i class="fa fa-long-arrow-right"></i></a>
                        </div>
                    </div>
                </div>
            `).join('');
        },

        // Mettre à jour les avantages (cercles de pourcentage)
        updateAdvantages(advantages) {
            const container = document.querySelector('.product-advantage .row:last-child');
            if (!container || !advantages?.length) return;

            container.innerHTML = advantages.map((adv, index) => `
                <div class="col-md-3 col-sm-6">
                    <div class="product-advantages-chart">
                        <div class="demo-${index + 1}" data-percent="${adv.percentage}"></div>
                        <p>${adv.title}</p>
                    </div>
                </div>
            `).join('');

            // Réinitialiser les cercles
            if (typeof $.fn.circlechart !== 'undefined') {
                advantages.forEach((adv, index) => {
                    $(`.demo-${index + 1}`).circlechart({
                        size: 150,
                        value: adv.percentage,
                        fill: { gradient: [adv.color || '#4CAF50', '#81C784'] }
                    });
                });
            }
        },

        // Initialiser le chargement dynamique
        async init() {
            const data = await this.loadSiteData();
            if (!data) return;

            // Mettre à jour les différentes sections si les données existent
            if (data.hero_slides) this.updateHeroSlides(data.hero_slides);
            if (data.services) this.updateServices(data.services);
            if (data.products) this.updateProducts(data.products);
            if (data.team_members) this.updateTeamMembers(data.team_members);
            if (data.advantages) this.updateAdvantages(data.advantages);
        }
    };
})();


// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    // Initialiser les formulaires
    AquaRacineForms.initAll();

    // Charger le contenu dynamique (décommenter quand l'API est prête)
    // AquaRacineContent.init();
});
