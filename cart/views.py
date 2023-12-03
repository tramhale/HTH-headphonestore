from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from datetime import datetime
from django.contrib import messages
from django.views import generic

from .carts import Cart
from .models import Coupon
from product.models import Product

class AddToCart(generic.View):
  def post(self, *args, **kwargs):
    product = get_object_or_404(Product, id=kwargs.get('product_id'))
    cart = Cart(self.request)
    cart.update(product.id, 1)
    return redirect('cart')
  
class CartItems(generic.TemplateView):
  template_name = 'cart/cart.html'

  def get(self, request, *args, **kwargs):
    product_id = request.GET.get('product_id', None)
    quantity = request.GET.get('quantity', None)
    clear = request.GET.get('clear', False)
    cart = Cart(request)
    print(cart.coupon, "coupon")

    if product_id and quantity:
      product = get_object_or_404(Product, id=product_id)
      if int(quantity) > 0:
        if product.in_stock:
          cart.update(int(product_id), int(quantity))
          return redirect('cart')
        else:
          messages.warning(request, "The product is not in stock anymore")
          return redirect('cart')
      else:
        cart.update(int(product_id), int(quantity))
        return redirect('cart')
    
    if clear:
      cart.clear()
      return redirect('cart')

    
    return super().get(request, *args, **kwargs)
  
class AddCoupon(generic.View):
  def post(self, *args, **kwargs):
    code = self.request.POST.get('coupon', '')
    coupon = Coupon.objects.filter(code__iexact=code, active=True)
    cart = Cart(self.request)

    if coupon.exists():
      coupon = coupon.first()
      current_date = datetime.date(timezone.now())
      active_date = coupon.active_date
      expiry_date = coupon.expiry_date

      if current_date > expiry_date:
        messages.warning(self.request, "The coupon expired")
        return redirect('cart')
      
      if current_date < active_date:
        messages.warning(self.request, "The coupon is yet to be available")
        return redirect('cart')
      if cart.total() < coupon.required_amount_to_use_coupon:
        messages.warning(self.request, f"You have to shop at least ${coupon.required_amount_to_use_coupon} to use this coupon code")
        return redirect('cart')
      
      cart.add_coupon(coupon.id)
      messages.success(self.request, "Your coupon has been included sucessfuly!")
      return redirect('cart')
    
    else:
      messages.warning(self.request, "Invalid coupon code")
      return redirect('cart')