from . import models


def populate_unrevisioned_name(cr, registry):
    cr.execute(
        "UPDATE vtt_car_repair_order "
        "SET unrevisioned_name = name "
        "WHERE unrevisioned_name is NULL"
    )
