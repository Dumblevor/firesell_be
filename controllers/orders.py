from http import HTTPStatus
from flask import Blueprint, jsonify, request, g
from marshmallow.exceptions import ValidationError
from middleware.secure_route import secure_route

from models.order import OrderModel
from models.product import ProductModel
from serializers.order_serializer import OrderSchema
from serializers.orderLine_serializer import OrderLineSchema


router = Blueprint("orders", __name__)
order_schema = OrderSchema()
orderLine_schema = OrderLineSchema()


@router.route("/allorders", methods=["GET"])
@secure_route
def get_orders():
    orders = OrderModel.query.all()
    return order_schema.jsonify(orders, many=True), HTTPStatus.OK


@router.route("/orders/<int:order_id>", methods=["GET"])
@secure_route
def get_an_order(order_id):
    order = OrderModel.query.get(order_id)

    if not order:
        return {"message": "order not found"}, HTTPStatus.NOT_FOUND
    return order_schema.jsonify(order), HTTPStatus.OK


@router.route("/neworder", methods=["POST"])
@secure_route
def create_order():
    total = 0
    order_dict = request.json
    print(order_dict)
    # for product in order_dict.product_id:
    #     getProduct = ProductModel.query.get(product)
    #     total += product.quantity * getProduct.price

    orderData = {
        "totalAmount": total,
        "orderStatus": "new"
    }

    try:
        order = order_schema.load(orderData)  # make order
        print(order)
    except ValidationError as e:
        return {"errors": e.messages, "message": "Something went wrong"}

    order.customer_id = g.current_customer.id
    savedOrder = order.save()

    for product in order_dict.products:
        orderLineData = {
            "product_id": product.product_id,
            "order_id": savedOrder.id,
            "quantity": product.quantity
        }

        newOrderLine = orderLine_schema.load(orderLineData)
        newOrderLineSaved = newOrderLine.save()
        print(newOrderLineSaved)

    print(g.current_customer.id)
    print(order.customer_id)

    return HTTPStatus.CREATED
