/**
 * Aqua-Racine - Système de panier avec paiement avance 50% et WhatsApp
 */

const AquaCart = {
    // Configuration
    config: {
        whatsappNumber: '+2250767203532', // Numéro WhatsApp support
        advancePercentage: 50, // Pourcentage d'avance requis
        deliveryFee: 1500, // Frais de livraison en FCFA
        currency: 'FCFA'
    },

    // Code promo actuel
    promo: {
        code: null,
        discount: null,
        participationId: null
    },

    // Initialisation
    init: function() {
        this.loadCart();
        this.updateCartBadge();
        this.bindEvents();
    },

    // Charger le panier depuis localStorage
    loadCart: function() {
        const cart = localStorage.getItem('aquaracine_cart');
        return cart ? JSON.parse(cart) : [];
    },

    // Sauvegarder le panier
    saveCart: function(cart) {
        localStorage.setItem('aquaracine_cart', JSON.stringify(cart));
        this.updateCartBadge();
    },

    // Ajouter un produit au panier
    addToCart: function(product) {
        const cart = this.loadCart();
        const existingItem = cart.find(item => item.id === product.id);

        if (existingItem) {
            existingItem.quantity += product.quantity || 1;
        } else {
            cart.push({
                id: product.id,
                name: product.name,
                price: parseFloat(product.price),
                image: product.image,
                unit: product.unit || '',
                quantity: product.quantity || 1
            });
        }

        this.saveCart(cart);
        this.showNotification('Produit ajouté au panier !', 'success');
        return cart;
    },

    // Supprimer un produit du panier
    removeFromCart: function(productId) {
        let cart = this.loadCart();
        cart = cart.filter(item => item.id !== productId);
        this.saveCart(cart);
        return cart;
    },

    // Mettre à jour la quantité
    updateQuantity: function(productId, quantity) {
        const cart = this.loadCart();
        const item = cart.find(item => item.id === productId);

        if (item) {
            item.quantity = Math.max(1, quantity);
            this.saveCart(cart);
        }
        return cart;
    },

    // Vider le panier
    clearCart: function() {
        localStorage.removeItem('aquaracine_cart');
        this.updateCartBadge();
    },

    // Calculer le sous-total
    getSubtotal: function() {
        const cart = this.loadCart();
        return cart.reduce((total, item) => total + (item.price * item.quantity), 0);
    },

    // Calculer la réduction appliquée
    getDiscount: function() {
        if (!this.promo.discount) return 0;

        const discount = this.promo.discount;

        // Si livraison gratuite
        if (discount.free_delivery) {
            return this.config.deliveryFee;
        }

        // Si réduction en pourcentage
        if (discount.type === 'discount' && discount.percent > 0) {
            // La réduction s'applique sur le sous-total (produits)
            return Math.ceil(this.getSubtotal() * (discount.percent / 100));
        }

        return 0;
    },

    // Obtenir les frais de livraison (peut être 0 si promo livraison gratuite)
    getDeliveryFee: function() {
        if (this.promo.discount && this.promo.discount.free_delivery) {
            return 0;
        }
        return this.config.deliveryFee;
    },

    // Calculer le total avec livraison et réduction
    getTotal: function() {
        const subtotal = this.getSubtotal();
        const delivery = this.getDeliveryFee();
        const discount = this.promo.discount && this.promo.discount.type === 'discount' ? this.getDiscount() : 0;
        return Math.max(0, subtotal + delivery - discount);
    },

    // Calculer l'avance (50%)
    getAdvance: function() {
        return Math.ceil(this.getTotal() * (this.config.advancePercentage / 100));
    },

    // Calculer le reste à payer
    getRemainder: function() {
        return this.getTotal() - this.getAdvance();
    },

    // Valider un code promo
    validatePromoCode: async function(code) {
        try {
            const response = await fetch('/api/promo/validate/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ code: code }),
            });

            const data = await response.json();

            if (data.valid) {
                this.promo.code = code.toUpperCase();
                this.promo.discount = data.discount;
                this.promo.participationId = data.participation_id;
                return { valid: true, message: data.message, discount: data.discount };
            } else {
                this.clearPromo();
                return { valid: false, message: data.message };
            }
        } catch (error) {
            console.error('Error validating promo code:', error);
            return { valid: false, message: 'Erreur de validation du code' };
        }
    },

    // Effacer le code promo
    clearPromo: function() {
        this.promo.code = null;
        this.promo.discount = null;
        this.promo.participationId = null;
    },

    // Marquer le code promo comme utilisé
    markPromoUsed: async function() {
        if (!this.promo.code) return;

        try {
            await fetch('/api/promo/mark-used/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ code: this.promo.code }),
            });
        } catch (error) {
            console.error('Error marking promo as used:', error);
        }
    },

    // Mettre à jour le badge du panier
    updateCartBadge: function() {
        const cart = this.loadCart();
        const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
        const badges = document.querySelectorAll('.aquaponic-cart span, .cart-badge, #floating-cart-count');
        badges.forEach(badge => {
            badge.textContent = totalItems;
        });

        // Afficher/masquer le bouton flottant
        const floatingCart = document.getElementById('floating-cart');
        if (floatingCart) {
            if (totalItems > 0) {
                floatingCart.classList.remove('hidden');
            } else {
                floatingCart.classList.add('hidden');
            }
        }
    },

    // Afficher une notification
    showNotification: function(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `cart-notification cart-notification-${type}`;
        notification.innerHTML = `
            <i class="fa ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
            <span>${message}</span>
        `;
        document.body.appendChild(notification);

        setTimeout(() => notification.classList.add('show'), 10);
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    },

    // Formater le prix
    formatPrice: function(price) {
        return new Intl.NumberFormat('fr-FR').format(price) + ' ' + this.config.currency;
    },

    // Générer le résumé de commande pour WhatsApp
    generateOrderSummary: function(customerInfo) {
        const cart = this.loadCart();
        let summary = `🛒 *NOUVELLE COMMANDE AQUA-RACINE*\n\n`;
        summary += `👤 *Client:* ${customerInfo.firstName} ${customerInfo.lastName}\n`;
        summary += `📞 *Téléphone:* ${customerInfo.phone}\n`;
        summary += `📧 *Email:* ${customerInfo.email}\n`;
        summary += `📍 *Adresse:* ${customerInfo.address}, ${customerInfo.city}\n`;
        if (customerInfo.commune) {
            summary += `🏘️ *Commune:* ${customerInfo.commune}\n`;
        }
        if (customerInfo.notes) {
            summary += `📝 *Instructions:* ${customerInfo.notes}\n`;
        }
        summary += `\n━━━━━━━━━━━━━━━━━━━━\n`;
        summary += `📦 *ARTICLES COMMANDÉS:*\n\n`;

        cart.forEach((item, index) => {
            summary += `${index + 1}. ${item.name}\n`;
            summary += `   Quantité: ${item.quantity}${item.unit ? ' ' + item.unit : ''}\n`;
            summary += `   Prix unitaire: ${this.formatPrice(item.price)}\n`;
            summary += `   Sous-total: ${this.formatPrice(item.price * item.quantity)}\n\n`;
        });

        summary += `━━━━━━━━━━━━━━━━━━━━\n`;
        summary += `💰 *RÉCAPITULATIF:*\n`;
        summary += `   Sous-total: ${this.formatPrice(this.getSubtotal())}\n`;

        // Afficher le code promo si appliqué
        if (this.promo.code && this.promo.discount) {
            const discount = this.promo.discount;
            if (discount.free_delivery) {
                summary += `   Livraison: ~${this.formatPrice(this.config.deliveryFee)}~ GRATUITE 🎁\n`;
                summary += `   🎟️ *Code promo: ${this.promo.code}*\n`;
                summary += `   ✨ *Livraison offerte !*\n`;
            } else if (discount.type === 'discount' && discount.percent > 0) {
                summary += `   Livraison: ${this.formatPrice(this.getDeliveryFee())}\n`;
                summary += `   🎟️ *Code promo: ${this.promo.code}*\n`;
                summary += `   ✨ *Réduction -${discount.percent}%: -${this.formatPrice(this.getDiscount())}*\n`;
            }
        } else {
            summary += `   Livraison: ${this.formatPrice(this.getDeliveryFee())}\n`;
        }

        summary += `   *TOTAL: ${this.formatPrice(this.getTotal())}*\n\n`;
        summary += `━━━━━━━━━━━━━━━━━━━━\n`;
        summary += `💳 *PAIEMENT:*\n`;
        summary += `   ✅ Avance payée (50%): ${this.formatPrice(this.getAdvance())}\n`;
        summary += `   ⏳ Reste à payer à la livraison: ${this.formatPrice(this.getRemainder())}\n\n`;
        summary += `━━━━━━━━━━━━━━━━━━━━\n`;
        summary += `📅 Date: ${new Date().toLocaleString('fr-FR')}\n`;
        summary += `\n_Merci pour votre commande !_`;

        return summary;
    },

    // Envoyer la commande via WhatsApp
    sendToWhatsApp: function(customerInfo) {
        const summary = this.generateOrderSummary(customerInfo);
        const encodedMessage = encodeURIComponent(summary);
        const whatsappUrl = `https://wa.me/${this.config.whatsappNumber.replace(/[^0-9]/g, '')}?text=${encodedMessage}`;

        // Ouvrir WhatsApp dans un nouvel onglet
        window.open(whatsappUrl, '_blank');

        return true;
    },

    // Lier les événements
    bindEvents: function() {
        // Boutons "Ajouter au panier"
        document.addEventListener('click', (e) => {
            const addBtn = e.target.closest('.add-to-cart-btn, .product-img-overlay .aquaponic-btn');
            if (addBtn) {
                e.preventDefault();
                const productCard = addBtn.closest('.single-product, .product-card');
                if (productCard) {
                    const product = {
                        id: productCard.dataset.productId || addBtn.dataset.productId,
                        name: productCard.dataset.productName || productCard.querySelector('.single-product-info p a, .product-name')?.textContent,
                        price: productCard.dataset.productPrice || parseFloat(productCard.querySelector('.single-product-info h4, .product-price')?.textContent.replace(/[^\d]/g, '')),
                        image: productCard.querySelector('img')?.src,
                        unit: productCard.dataset.productUnit || ''
                    };

                    if (product.id && product.name && product.price) {
                        this.addToCart(product);
                    }
                }
            }
        });
    }
};

// Rendu du panier sur la page panier
const CartRenderer = {
    render: function() {
        const cart = AquaCart.loadCart();
        const cartContent = document.getElementById('cart-content');
        const emptyCart = document.getElementById('empty-cart');
        const cartItems = document.getElementById('cart-items');
        const cartMobileItems = document.getElementById('cart-mobile-items');

        if (cart.length === 0) {
            if (emptyCart) emptyCart.style.display = 'block';
            if (cartContent) cartContent.style.display = 'none';
            return;
        }

        if (emptyCart) emptyCart.style.display = 'none';
        if (cartContent) cartContent.style.display = 'block';

        // Rendu table desktop
        if (cartItems) {
            cartItems.innerHTML = cart.map(item => `
                <tr data-id="${item.id}">
                    <td>
                        <div class="cart-product">
                            <img src="${item.image || '/static/img/product/default.jpg'}" alt="${item.name}">
                            <div class="cart-product-info">
                                <h5>${item.name}</h5>
                            </div>
                        </div>
                    </td>
                    <td>${AquaCart.formatPrice(item.price)}${item.unit ? '/' + item.unit : ''}</td>
                    <td>
                        <div class="cart-qty">
                            <button class="qty-minus" data-id="${item.id}">-</button>
                            <input type="number" value="${item.quantity}" min="1" class="qty-input" data-id="${item.id}">
                            <button class="qty-plus" data-id="${item.id}">+</button>
                        </div>
                    </td>
                    <td><strong>${AquaCart.formatPrice(item.price * item.quantity)}</strong></td>
                    <td><i class="fa fa-trash remove-item" data-id="${item.id}"></i></td>
                </tr>
            `).join('');

            this.bindCartEvents(cartItems);
        }

        // Rendu cartes mobile
        if (cartMobileItems) {
            cartMobileItems.innerHTML = cart.map(item => `
                <div class="cart-mobile-card" data-id="${item.id}">
                    <div class="cart-mobile-card-header">
                        <img src="${item.image || '/static/img/product/default.jpg'}" alt="${item.name}" class="cart-mobile-card-img">
                        <div class="cart-mobile-card-info">
                            <h5>${item.name}</h5>
                            <span class="price">${AquaCart.formatPrice(item.price)}${item.unit ? '/' + item.unit : ''}</span>
                        </div>
                    </div>
                    <div class="cart-mobile-card-footer">
                        <div class="cart-mobile-card-qty">
                            <button class="qty-minus" data-id="${item.id}">-</button>
                            <input type="number" value="${item.quantity}" min="1" class="qty-input" data-id="${item.id}">
                            <button class="qty-plus" data-id="${item.id}">+</button>
                        </div>
                        <div class="cart-mobile-card-total">
                            <span class="total-price">${AquaCart.formatPrice(item.price * item.quantity)}</span>
                            <button class="remove-btn remove-item" data-id="${item.id}"><i class="fa fa-trash"></i></button>
                        </div>
                    </div>
                </div>
            `).join('');

            this.bindCartEvents(cartMobileItems);
        }

        // Mettre à jour les totaux
        document.getElementById('subtotal')?.textContent && (document.getElementById('subtotal').textContent = AquaCart.formatPrice(AquaCart.getSubtotal()));
        document.getElementById('shipping')?.textContent && (document.getElementById('shipping').textContent = AquaCart.formatPrice(AquaCart.config.deliveryFee));
        document.getElementById('total')?.textContent && (document.getElementById('total').textContent = AquaCart.formatPrice(AquaCart.getTotal()));
    },

    bindCartEvents: function(container) {
        const self = this;

        container.querySelectorAll('.qty-minus').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.dataset.id;
                const input = container.querySelector(`.qty-input[data-id="${id}"]`);
                const newQty = Math.max(1, parseInt(input.value) - 1);
                AquaCart.updateQuantity(id, newQty);
                self.render();
            });
        });

        container.querySelectorAll('.qty-plus').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.dataset.id;
                const input = container.querySelector(`.qty-input[data-id="${id}"]`);
                AquaCart.updateQuantity(id, parseInt(input.value) + 1);
                self.render();
            });
        });

        container.querySelectorAll('.qty-input').forEach(input => {
            input.addEventListener('change', () => {
                AquaCart.updateQuantity(input.dataset.id, parseInt(input.value) || 1);
                self.render();
            });
        });

        container.querySelectorAll('.remove-item').forEach(btn => {
            btn.addEventListener('click', () => {
                AquaCart.removeFromCart(btn.dataset.id);
                self.render();
            });
        });
    }
};

// Rendu du checkout
const CheckoutRenderer = {
    render: function() {
        const cart = AquaCart.loadCart();
        const orderItems = document.getElementById('order-items');

        if (cart.length === 0) {
            if (orderItems) {
                orderItems.innerHTML = '<p class="text-center" style="color: #888;">Aucun article dans le panier</p>';
            }
            return;
        }

        if (orderItems) {
            orderItems.innerHTML = cart.map(item => `
                <div class="order-item">
                    <span>${item.name} × ${item.quantity}</span>
                    <span>${AquaCart.formatPrice(item.price * item.quantity)}</span>
                </div>
            `).join('');
        }

        // Totaux - utiliser getDeliveryFee() pour prendre en compte les promos
        const subtotal = document.getElementById('order-subtotal');
        const shipping = document.getElementById('order-shipping');
        const total = document.getElementById('order-total');
        const advance = document.getElementById('order-advance');
        const remainder = document.getElementById('order-remainder');
        const checkoutAdvance = document.getElementById('checkout-advance');
        const checkoutRemainder = document.getElementById('checkout-remainder');

        if (subtotal) subtotal.textContent = AquaCart.formatPrice(AquaCart.getSubtotal());
        if (shipping) shipping.textContent = AquaCart.formatPrice(AquaCart.getDeliveryFee());
        if (total) total.textContent = AquaCart.formatPrice(AquaCart.getTotal());
        if (advance) advance.textContent = AquaCart.formatPrice(AquaCart.getAdvance());
        if (remainder) remainder.textContent = AquaCart.formatPrice(AquaCart.getRemainder());
        if (checkoutAdvance) checkoutAdvance.textContent = AquaCart.formatPrice(AquaCart.getAdvance());
        if (checkoutRemainder) checkoutRemainder.textContent = AquaCart.formatPrice(AquaCart.getRemainder());
    }
};

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    AquaCart.init();

    // Page panier
    if (document.getElementById('cart-items')) {
        CartRenderer.render();
    }

    // Page checkout - only render if not handled by checkout.html custom script
    // The checkout page has its own script that handles promo codes
    // We detect this by checking for the promo-code-input element
    if (document.getElementById('order-items') && !document.getElementById('promo-code-input')) {
        CheckoutRenderer.render();
    }
});
