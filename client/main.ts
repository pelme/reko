import $ from "jquery"

interface CartItem {
  productId: string
  sellerId: string
  amount: number
}

class Cart {
  public items: CartItem[]

  constructor() {
    try {
      this.items = JSON.parse(localStorage.getItem("cart") || "[]")
    } catch {
      this.items = []
    }
    this._refresh()
  }

  productCount() {
    return this.items.map((item) => item.amount).reduce((sum, item) => sum + item, 0)
  }

  sellerCount() {
    return new Set(this.items.map((item) => item.sellerId)).size
  }

  add(productId: string, sellerId: string, amount: number) {
    this.items.push({ productId, sellerId, amount })
    this._persist()
    this._refresh()
  }

  _refresh() {
    const cartEl = $("#cart .container")

    cartEl.text(
      this.items.length
        ? `${this.productCount()} varor från ${this.sellerCount()} producenter`
        : "Inga varor.",
    )
  }
  _persist() {
    localStorage.setItem("cart", JSON.stringify(this.items))
  }
}

$(() => {
  const cart = new Cart()

  $("body").on("submit", ".product-form", (e) => {
    const $form = $(e.target)

    cart.add(
      $form.find("[name=productId]").val(),
      $form.find("[name=sellerId]").val(),
      parseInt($form.find("[name=amount]").val() || "0"),
    )

    e.stopPropagation()
    e.preventDefault()
  })
})
