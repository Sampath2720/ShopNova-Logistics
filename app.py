import os

from flask import Flask, jsonify, render_template

app = Flask(__name__)

APP_ENV = os.getenv("APP_ENV", "LOCAL")
APP_VERSION = os.getenv("APP_VERSION", "2.0.0")


warehouses = [
    {
        "warehouse_id": "WH001",
        "name": "ShopNova Chennai Fulfilment Center",
        "location": "Chennai",
        "capacity": 5000,
        "status": "Operational"
    },
    {
        "warehouse_id": "WH002",
        "name": "ShopNova Hyderabad Distribution Center",
        "location": "Hyderabad",
        "capacity": 3500,
        "status": "Operational"
    }
]


drivers = [
    {
        "driver_id": "DRV001",
        "name": "Rajesh Kumar",
        "vehicle": "TN09AB1234",
        "shipments_assigned": 2,
        "status": "On Delivery"
    },
    {
        "driver_id": "DRV002",
        "name": "Kumar R",
        "vehicle": "TS08CD5678",
        "shipments_assigned": 1,
        "status": "Available"
    },
    {
        "driver_id": "DRV003",
        "name": "Ramesh B",
        "vehicle": "TN10EF9012",
        "shipments_assigned": 2,
        "status": "On Delivery"
    }
]


shipments = [
    {
        "shipment_id": "SHIP001",
        "order_id": "ORD1001",
        "product": "Mobile Phone",
        "warehouse": "Chennai",
        "destination": "Hyderabad",
        "driver": "Rajesh Kumar",
        "status": "Packed",
        "last_updated": "05-Oct-2026 09:15"
    },
    {
        "shipment_id": "SHIP002",
        "order_id": "ORD1002",
        "product": "Laptop",
        "warehouse": "Hyderabad",
        "destination": "Bengaluru",
        "driver": "Kumar R",
        "status": "In Transit",
        "last_updated": "05-Oct-2026 10:30"
    },
    {
        "shipment_id": "SHIP003",
        "order_id": "ORD1003",
        "product": "Smart Television",
        "warehouse": "Chennai",
        "destination": "Coimbatore",
        "driver": "Ramesh B",
        "status": "Delivered",
        "last_updated": "05-Oct-2026 11:45"
    },
    {
        "shipment_id": "SHIP004",
        "order_id": "ORD1004",
        "product": "Tablet",
        "warehouse": "Hyderabad",
        "destination": "Vijayawada",
        "driver": "Rajesh Kumar",
        "status": "Packed",
        "last_updated": "05-Oct-2026 12:20"
    },
    {
        "shipment_id": "SHIP005",
        "order_id": "ORD1005",
        "product": "Computer Monitor",
        "warehouse": "Chennai",
        "destination": "Madurai",
        "driver": "Ramesh B",
        "status": "Out For Delivery",
        "last_updated": "05-Oct-2026 13:10"
    }
]


def count_shipments_by_status(status):
    return sum(
        1
        for shipment in shipments
        if shipment["status"] == status
    )


@app.route("/")
def dashboard():
    return render_template(
        "index.html",
        app_env=APP_ENV,
        app_version=APP_VERSION,
        shipments=shipments,
        drivers=drivers,
        warehouses=warehouses,
        total_shipments=len(shipments),
        packed=count_shipments_by_status("Packed"),
        in_transit=count_shipments_by_status("In Transit"),
        out_for_delivery=count_shipments_by_status("Out For Delivery"),
        delivered=count_shipments_by_status("Delivered")
    )


@app.route("/api/shipments")
def get_shipments():
    return jsonify(
        {
            "environment": APP_ENV,
            "version": APP_VERSION,
            "count": len(shipments),
            "shipments": shipments
        }
    )


@app.route("/api/drivers")
def get_drivers():
    return jsonify(
        {
            "environment": APP_ENV,
            "count": len(drivers),
            "drivers": drivers
        }
    )


@app.route("/api/warehouses")
def get_warehouses():
    return jsonify(
        {
            "environment": APP_ENV,
            "count": len(warehouses),
            "warehouses": warehouses
        }
    )


@app.route("/api/shipments/<shipment_id>")
def track_shipment(shipment_id):
    shipment = next(
        (
            shipment
            for shipment in shipments
            if shipment["shipment_id"] == shipment_id.upper()
        ),
        None
    )

    if shipment is None:
        return jsonify(
            {
                "status": "error",
                "message": f"Shipment {shipment_id} was not found"
            }
        ), 404

    return jsonify(
        {
            "status": "success",
            "environment": APP_ENV,
            "shipment": shipment
        }
    )


@app.route("/health")
def health():
    return jsonify(
        {
            "status": "healthy",
            "application": "shopnova-logistics",
            "environment": APP_ENV,
            "version": APP_VERSION,
            "shipments_loaded": len(shipments)
        }
    ), 200


@app.route("/ready")
def readiness():
    data_loaded = (
        len(shipments) > 0
        and len(drivers) > 0
        and len(warehouses) > 0
    )

    if data_loaded:
        return jsonify(
            {
                "status": "ready",
                "environment": APP_ENV,
                "version": APP_VERSION
            }
        ), 200

    return jsonify(
        {
            "status": "not-ready",
            "environment": APP_ENV
        }
    ), 503


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=7070,
        debug=False
    )
