from __future__ import annotations

import json
import re
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

PORT = 8000

# ============================================================
# WASTE MANAGEMENT DATA
# ============================================================

WASTE_CATEGORIES = {
    "Organic Waste": {
        "bin_color": "Green",
        "acceptable_items": [
            "Food scraps",
            "Fruit and vegetable peels",
            "Garden waste",
            "Compostable organic material",
        ],
        "unacceptable_items": [
            "Plastic",
            "Glass",
            "Metal",
            "Chemicals",
        ],
        "preparation": "Remove plastic packaging and other non-organic materials.",
        "disposal_method": "Place in the green organic-waste bin.",
    },
    "Recyclables": {
        "bin_color": "Blue",
        "acceptable_items": [
            "Paper",
            "Cardboard",
            "Plastic containers",
            "Metal cans",
            "Clean recyclable packaging",
        ],
        "unacceptable_items": [
            "Food-contaminated waste",
            "Hazardous waste",
            "Medical waste",
        ],
        "preparation": "Empty, rinse, and flatten recyclable containers where appropriate.",
        "disposal_method": "Place in the blue recycling bin.",
    },
    "Paper & Cardboard": {
        "bin_color": "Blue",
        "acceptable_items": [
            "Newspapers",
            "Office paper",
            "Cardboard boxes",
            "Paper bags",
            "Envelopes",
        ],
        "unacceptable_items": [
            "Wet paper",
            "Food-soiled paper",
            "Wax-coated paper",
        ],
        "preparation": "Keep paper clean and dry. Flatten cardboard boxes.",
        "disposal_method": "Place in the blue recycling bin.",
    },
    "Plastics & Packaging": {
        "bin_color": "Blue",
        "acceptable_items": [
            "Plastic bottles",
            "Plastic containers",
            "Clean packaging",
        ],
        "unacceptable_items": [
            "Hazardous chemical containers",
            "Medical waste",
            "Heavily contaminated plastics",
        ],
        "preparation": "Empty and rinse containers before recycling.",
        "disposal_method": "Place accepted plastics in the recycling bin.",
    },
    "Glass": {
        "bin_color": "Blue",
        "acceptable_items": [
            "Glass bottles",
            "Glass jars",
        ],
        "unacceptable_items": [
            "Broken window glass",
            "Mirrors",
            "Ceramics",
            "Heat-resistant cookware",
        ],
        "preparation": "Empty containers and handle broken glass carefully.",
        "disposal_method": "Place accepted glass in the designated recycling container.",
    },
    "E-Waste & Electronics": {
        "bin_color": "Special E-Waste Container",
        "acceptable_items": [
            "Computers",
            "Laptops",
            "Mobile phones",
            "Televisions",
            "Small electronic appliances",
        ],
        "unacceptable_items": [
            "Regular household waste",
            "Food waste",
            "Loose hazardous chemicals",
        ],
        "preparation": "Remove personal data from devices when possible.",
        "disposal_method": "Take electronics to the designated E-Waste Hub.",
    },
    "Hazardous Waste": {
        "bin_color": "Hazardous Waste Container",
        "acceptable_items": [
            "Batteries",
            "Paint",
            "Chemicals",
            "Motor oil",
            "Household hazardous products",
        ],
        "unacceptable_items": [
            "Regular household waste",
            "Organic waste",
            "Normal recyclables",
        ],
        "preparation": "Keep hazardous products in their original containers where possible and do not mix chemicals.",
        "disposal_method": "Take hazardous waste to the designated hazardous-waste drop-off facility.",
    },
    "Medical Waste": {
        "bin_color": "Medical Waste Container",
        "acceptable_items": [
            "Used medical supplies",
            "Expired medicines",
            "Sharps in approved containers",
        ],
        "unacceptable_items": [
            "Regular household recycling",
            "Organic waste",
        ],
        "preparation": "Keep medical waste separated from normal household waste.",
        "disposal_method": "Use an approved medical-waste collection or drop-off service.",
    },
    "Bulky Items": {
        "bin_color": "Bulk Pickup",
        "acceptable_items": [
            "Furniture",
            "Couches",
            "Mattresses",
            "Large household items",
            "Tables",
        ],
        "unacceptable_items": [
            "Hazardous chemicals",
            "Medical waste",
            "Regular household bags",
        ],
        "preparation": "Keep bulky items accessible for collection and follow the municipality's booking instructions.",
        "disposal_method": "Book a bulky-item pickup service.",
    },
}


PICKUP_SCHEDULE = [
    {
        "zone": "Zone A - North",
        "waste_type": "Organic",
        "bin_color": "Green",
        "days": ["Monday", "Thursday"],
        "time_window": "7:00 AM - 5:00 PM",
        "instructions": "Place the bin at the curb before 7:00 AM.",
    },
    {
        "zone": "Zone A - North",
        "waste_type": "Recyclables",
        "bin_color": "Blue",
        "days": ["Tuesday"],
        "time_window": "7:00 AM - 5:00 PM",
        "instructions": "Place clean and dry recyclables at the curb.",
    },
    {
        "zone": "Zone A - North",
        "waste_type": "General Waste",
        "bin_color": "Black",
        "days": ["Wednesday", "Saturday"],
        "time_window": "7:00 AM - 5:00 PM",
        "instructions": "Place general waste in the black bin.",
    },

    {
        "zone": "Zone B - South",
        "waste_type": "Organic",
        "bin_color": "Green",
        "days": ["Tuesday", "Friday"],
        "time_window": "7:00 AM - 5:00 PM",
        "instructions": "Place the bin at the curb before collection.",
    },
    {
        "zone": "Zone B - South",
        "waste_type": "Recyclables",
        "bin_color": "Blue",
        "days": ["Wednesday"],
        "time_window": "7:00 AM - 5:00 PM",
        "instructions": "Only accepted clean recyclable materials should be placed in the bin.",
    },
    {
        "zone": "Zone B - South",
        "waste_type": "General Waste",
        "bin_color": "Black",
        "days": ["Thursday", "Saturday"],
        "time_window": "7:00 AM - 5:00 PM",
        "instructions": "Use the black bin for general household waste.",
    },

    {
        "zone": "Zone C - East",
        "waste_type": "Organic",
        "bin_color": "Green",
        "days": ["Monday", "Friday"],
        "time_window": "7:00 AM - 5:00 PM",
        "instructions": "Place the green bin at the curb before collection.",
    },
    {
        "zone": "Zone C - East",
        "waste_type": "Recyclables",
        "bin_color": "Blue",
        "days": ["Tuesday"],
        "time_window": "7:00 AM - 5:00 PM",
        "instructions": "Rinse containers and keep recyclables loose where required.",
    },
    {
        "zone": "Zone C - East",
        "waste_type": "General Waste",
        "bin_color": "Black",
        "days": ["Wednesday", "Saturday"],
        "time_window": "7:00 AM - 5:00 PM",
        "instructions": "Use the black bin for general waste.",
    },

    {
        "zone": "Zone D - West",
        "waste_type": "Organic",
        "bin_color": "Green",
        "days": ["Tuesday", "Friday"],
        "time_window": "7:00 AM - 5:00 PM",
        "instructions": "Place organic waste in the green bin.",
    },
    {
        "zone": "Zone D - West",
        "waste_type": "Recyclables",
        "bin_color": "Blue",
        "days": ["Thursday"],
        "time_window": "7:00 AM - 5:00 PM",
        "instructions": "Place clean recyclables at the curb.",
    },
    {
        "zone": "Zone D - West",
        "waste_type": "General Waste",
        "bin_color": "Black",
        "days": ["Monday", "Saturday"],
        "time_window": "7:00 AM - 5:00 PM",
        "instructions": "Use the black bin for general waste.",
    },

    {
        "zone": "Zone E - Central",
        "waste_type": "Organic",
        "bin_color": "Green",
        "days": ["Monday", "Thursday"],
        "time_window": "7:00 AM - 5:00 PM",
        "instructions": "Place organic waste in the green bin.",
    },
    {
        "zone": "Zone E - Central",
        "waste_type": "Recyclables",
        "bin_color": "Blue",
        "days": ["Wednesday"],
        "time_window": "7:00 AM - 5:00 PM",
        "instructions": "Place clean recyclable materials in the blue bin.",
    },
    {
        "zone": "Zone E - Central",
        "waste_type": "General Waste",
        "bin_color": "Black",
        "days": ["Tuesday", "Friday"],
        "time_window": "7:00 AM - 5:00 PM",
        "instructions": "Use the black bin for general household waste.",
    },
]


FACILITIES = {
    "Recycling Center": {
        "name": "Municipal Recycling Center",
        "address": "12 Green Avenue",
        "weekday_hours": "8:00 AM - 6:00 PM",
        "weekend_hours": "9:00 AM - 4:00 PM",
        "accepted_items": "Paper, cardboard, plastics, glass, and metals",
        "incentives_or_fees": "No standard drop-off fee",
        "contact": "Municipal Waste Department",
    },
    "Composting Facility": {
        "name": "Municipal Composting Facility",
        "address": "25 Eco Park Road",
        "weekday_hours": "8:00 AM - 5:00 PM",
        "weekend_hours": "9:00 AM - 3:00 PM",
        "accepted_items": "Food waste, garden waste, and other accepted organic material",
        "incentives_or_fees": "Standard residential drop-off",
        "contact": "Municipal Waste Department",
    },
    "E-Waste Hub": {
        "name": "Municipal E-Waste Hub",
        "address": "40 Technology Lane",
        "weekday_hours": "9:00 AM - 5:00 PM",
        "weekend_hours": "10:00 AM - 3:00 PM",
        "accepted_items": "Computers, phones, televisions, batteries, and electronics",
        "incentives_or_fees": "Residential electronics accepted",
        "contact": "Municipal Waste Department",
    },
    "Transfer Station": {
        "name": "Municipal Transfer Station",
        "address": "50 Industrial Road",
        "weekday_hours": "7:00 AM - 6:00 PM",
        "weekend_hours": "8:00 AM - 4:00 PM",
        "accepted_items": "General waste and approved bulky materials",
        "incentives_or_fees": "Fees may apply to certain loads",
        "contact": "Municipal Waste Department",
    },
    "Hazardous Drop-off": {
        "name": "Hazardous Waste Drop-off Depot",
        "address": "75 Environmental Way",
        "weekday_hours": "9:00 AM - 5:00 PM",
        "weekend_hours": "10:00 AM - 2:00 PM",
        "accepted_items": "Batteries, paint, chemicals, oils, and other approved hazardous materials",
        "incentives_or_fees": "Residential drop-off available",
        "contact": "Municipal Waste Department",
    },
    "Main Administrative Office": {
        "name": "Municipal Waste Management Office",
        "address": "1 Civic Center Road",
        "weekday_hours": "9:00 AM - 5:00 PM",
        "weekend_hours": "Closed",
        "accepted_items": "Administrative enquiries and service requests",
        "incentives_or_fees": "Not applicable",
        "contact": "Municipal Waste Department",
    },
}


SERVICE_REQUESTS = {
    "Bulk Pickup": {
        "service": "Bulk Pickup",
        "description": "Collection of large household items such as furniture and mattresses.",
        "lead_time": "Book in advance according to municipal availability.",
        "fee": "Fees may apply depending on the item and service.",
        "procedure": [
            "Contact the municipal waste department.",
            "Provide your address and details of the items.",
            "Schedule an available pickup date.",
            "Place the items in the designated collection area.",
        ],
        "contact": "Municipal Waste Department",
    },
    "Extra Bin Request": {
        "service": "Extra Bin Request",
        "description": "Request an additional waste or recycling bin.",
        "lead_time": "Processing time depends on municipal availability.",
        "fee": "Fees may apply.",
        "procedure": [
            "Contact the municipal waste department.",
            "Provide your address.",
            "Specify the type and number of bins required.",
            "Follow the department's delivery instructions.",
        ],
        "contact": "Municipal Waste Department",
    },
    "Hazardous Disposal": {
        "service": "Hazardous Disposal",
        "description": "Information and assistance for disposing of household hazardous waste.",
        "lead_time": "Check the drop-off facility schedule before visiting.",
        "fee": "Depends on the material and service.",
        "procedure": [
            "Identify the hazardous material.",
            "Keep it separated from normal household waste.",
            "Contact the municipal waste department if unsure.",
            "Take it to an approved hazardous-waste facility.",
        ],
        "contact": "Municipal Waste Department",
    },
    "Illegal Dumping Report": {
        "service": "Illegal Dumping Report",
        "description": "Report suspected illegal dumping or fly-tipping.",
        "lead_time": "Reports can be submitted to the municipal waste department.",
        "fee": "No standard reporting fee.",
        "procedure": [
            "Record the location of the suspected dumping.",
            "Provide relevant details to the municipal authority.",
            "Submit the report through the appropriate municipal channel.",
        ],
        "contact": "Municipal Waste Department",
    },
    "Bin Replacement": {
        "service": "Bin Replacement",
        "description": "Request replacement of a broken, damaged, or stolen waste bin.",
        "lead_time": "Replacement timing depends on municipal availability.",
        "fee": "Fees may apply depending on the circumstances.",
        "procedure": [
            "Contact the municipal waste department.",
            "Provide your address and bin details.",
            "Explain whether the bin is broken, damaged, or missing.",
            "Follow the replacement instructions.",
        ],
        "contact": "Municipal Waste Department",
    },
}


# ============================================================
# DATA FUNCTIONS
# ============================================================

def get_disposal_guidelines(category=None):
    if category is None:
        return {
            "status": "success",
            "categories": list(WASTE_CATEGORIES.keys()),
        }

    if category not in WASTE_CATEGORIES:
        return {
            "status": "error",
            "message": f"Unknown waste category: {category}",
        }

    return {
        "status": "success",
        "guidelines": WASTE_CATEGORIES[category],
    }


def get_facility_info(facility_type=None):
    if facility_type is None:
        return {
            "status": "success",
            "facilities": list(FACILITIES.keys()),
        }

    if facility_type not in FACILITIES:
        return {
            "status": "error",
            "message": f"Unknown facility: {facility_type}",
        }

    return {
        "status": "success",
        "info": FACILITIES[facility_type],
    }


def get_pickup_schedule(zone=None, waste_type=None):
    schedules = PICKUP_SCHEDULE

    if zone:
        schedules = [
            item
            for item in schedules
            if item["zone"].lower() == zone.lower()
        ]

    if waste_type:
        schedules = [
            item
            for item in schedules
            if item["waste_type"].lower() == waste_type.lower()
        ]

    return {
        "status": "success",
        "schedules": schedules,
    }


def get_service_request_info(service_type=None):
    if service_type is None:
        return {
            "status": "success",
            "services": list(SERVICE_REQUESTS.keys()),
        }

    if service_type not in SERVICE_REQUESTS:
        return {
            "status": "error",
            "message": f"Unknown service: {service_type}",
        }

    return {
        "status": "success",
        "info": SERVICE_REQUESTS[service_type],
    }


# ============================================================
# CHAT PROCESSING
# ============================================================

def process_user_chat(message: str) -> str:
    msg_lower = message.lower().strip()

    # --------------------------------------------------------
    # Pickup schedule
    # --------------------------------------------------------

    if any(k in msg_lower for k in [
        "schedule",
        "pickup",
        "when is",
        "collection",
        "trash day",
        "zone",
    ]):
        zone_match = re.search(r"zone\s*([a-e])", msg_lower)

        if zone_match:
            zone_map = {
                "A": "Zone A - North",
                "B": "Zone B - South",
                "C": "Zone C - East",
                "D": "Zone D - West",
                "E": "Zone E - Central",
            }

            zone_name = zone_map[zone_match.group(1).upper()]
            waste_type = None

            if "organic" in msg_lower or "food" in msg_lower:
                waste_type = "Organic"

            elif (
                "recycl" in msg_lower
                or "paper" in msg_lower
                or "cardboard" in msg_lower
            ):
                waste_type = "Recyclables"

            elif "hazard" in msg_lower:
                waste_type = "Hazardous"

            elif (
                "general" in msg_lower
                or "black bin" in msg_lower
                or "trash" in msg_lower
            ):
                waste_type = "General Waste"

            res = get_pickup_schedule(zone_name, waste_type)

            if res["schedules"]:
                lines = [
                    f"### Waste Collection Schedule for {zone_name}",
                    "",
                ]

                for item in res["schedules"]:
                    lines.append(
                        f"- {item['waste_type']} "
                        f"({item['bin_color']}): "
                        f"{', '.join(item['days'])} "
                        f"between {item['time_window']}."
                    )

                    lines.append(
                        f"  Instructions: {item['instructions']}"
                    )

                    lines.append("")

                return "\n".join(lines)

        return (
            "### Collection Schedule\n\n"
            "Please specify your municipal zone:\n\n"
            "- Zone A\n"
            "- Zone B\n"
            "- Zone C\n"
            "- Zone D\n"
            "- Zone E"
        )

    # --------------------------------------------------------
    # Disposal guidelines
    # --------------------------------------------------------

    if any(k in msg_lower for k in [
        "sort",
        "recycle",
        "dispose",
        "how to",
        "where to put",
        "battery",
        "batteries",
        "paint",
        "e-waste",
        "electronics",
        "glass",
        "plastic",
        "paper",
        "cardboard",
        "organic",
        "medical",
        "sharps",
        "furniture",
        "couch",
        "mattress",
    ]):
        category = None

        if any(k in msg_lower for k in [
            "e-waste",
            "electronic",
            "laptop",
            "phone",
            "tv",
            "appliance",
            "computer",
        ]):
            category = "E-Waste & Electronics"

        elif any(k in msg_lower for k in [
            "paint",
            "chemical",
            "hazard",
            "battery",
            "batteries",
            "oil",
            "cleaner",
        ]):
            category = "Hazardous Waste"

        elif any(k in msg_lower for k in [
            "food",
            "compost",
            "organic",
            "yard",
            "peel",
            "scrap",
        ]):
            category = "Organic Waste"

        elif any(k in msg_lower for k in [
            "plastic",
            "can",
            "bottle",
            "packaging",
        ]):
            category = "Plastics & Packaging"

        elif any(k in msg_lower for k in [
            "paper",
            "cardboard",
            "box",
            "envelope",
        ]):
            category = "Paper & Cardboard"

        elif any(k in msg_lower for k in [
            "glass",
            "jar",
        ]):
            category = "Glass"

        elif any(k in msg_lower for k in [
            "couch",
            "mattress",
            "furniture",
            "bulky",
            "table",
        ]):
            category = "Bulky Items"

        elif any(k in msg_lower for k in [
            "needle",
            "syringe",
            "medical",
            "sharp",
            "medicine",
        ]):
            category = "Medical Waste"

        if category:
            res = get_disposal_guidelines(category)

            if res["status"] == "success":
                g = res["guidelines"]

                return (
                    f"### Disposal Guidelines for {category}\n\n"
                    f"- Designated Bin / Container: {g['bin_color']}\n"
                    f"- Acceptable Items: {', '.join(g['acceptable_items'])}\n"
                    f"- Unacceptable Items: {', '.join(g['unacceptable_items'])}\n"
                    f"- Preparation: {g['preparation']}\n"
                    f"- Disposal Method: {g['disposal_method']}"
                )

        categories = "\n".join(
            f"- {category}"
            for category in WASTE_CATEGORIES
        )

        return (
            "### Available Waste Categories\n\n"
            f"{categories}\n\n"
            "Which item or category would you like help sorting?"
        )

    # --------------------------------------------------------
    # Facility information
    # --------------------------------------------------------

    if any(k in msg_lower for k in [
        "facility",
        "center",
        "depot",
        "location",
        "address",
        "hours",
        "open",
    ]):
        fac_type = None

        if "recycl" in msg_lower:
            fac_type = "Recycling Center"

        elif "compost" in msg_lower:
            fac_type = "Composting Facility"

        elif (
            "e-waste" in msg_lower
            or "battery" in msg_lower
            or "tech" in msg_lower
        ):
            fac_type = "E-Waste Hub"

        elif (
            "transfer" in msg_lower
            or "debris" in msg_lower
        ):
            fac_type = "Transfer Station"

        elif (
            "hazard" in msg_lower
            or "eco depot" in msg_lower
            or "chemical" in msg_lower
        ):
            fac_type = "Hazardous Drop-off"

        elif (
            "office" in msg_lower
            or "headquarters" in msg_lower
            or "admin" in msg_lower
        ):
            fac_type = "Main Administrative Office"

        if fac_type:
            res = get_facility_info(fac_type)

            if res["status"] == "success":
                info = res["info"]

                return (
                    f"### {info['name']}\n\n"
                    f"- Address: {info['address']}\n"
                    f"- Weekday Hours: {info['weekday_hours']}\n"
                    f"- Weekend Hours: {info['weekend_hours']}\n"
                    f"- Accepted Items: {info['accepted_items']}\n"
                    f"- Fees / Incentives: {info['incentives_or_fees']}\n"
                    f"- Contact: {info['contact']}"
                )

        return (
            "### Available Facilities\n\n"
            "- Recycling Center\n"
            "- Composting Facility\n"
            "- E-Waste Hub\n"
            "- Transfer Station\n"
            "- Hazardous Drop-off\n"
            "- Main Administrative Office\n\n"
            "Which facility would you like details for?"
        )

    # --------------------------------------------------------
    # Service requests
    # --------------------------------------------------------

    if any(k in msg_lower for k in [
        "bulk",
        "request",
        "book",
        "extra bin",
        "stolen",
        "broken",
        "dumping",
        "replacement",
    ]):
        srv_type = None

        if "bulk" in msg_lower or "furniture" in msg_lower:
            srv_type = "Bulk Pickup"

        elif (
            "extra bin" in msg_lower
            or "additional bin" in msg_lower
        ):
            srv_type = "Extra Bin Request"

        elif "hazard" in msg_lower:
            srv_type = "Hazardous Disposal"

        elif (
            "dumping" in msg_lower
            or "fly-tipping" in msg_lower
            or "illegal" in msg_lower
        ):
            srv_type = "Illegal Dumping Report"

        elif (
            "replacement" in msg_lower
            or "broken" in msg_lower
            or "stolen" in msg_lower
        ):
            srv_type = "Bin Replacement"

        if srv_type:
            res = get_service_request_info(srv_type)

            if res["status"] == "success":
                info = res["info"]

                lines = [
                    f"### {info['service']}",
                    "",
                    f"- Description: {info['description']}",
                    f"- Lead Time: {info['lead_time']}",
                    f"- Fee Structure: {info['fee']}",
                    "",
                    "- Steps:",
                ]

                for index, step in enumerate(info["procedure"], 1):
                    lines.append(f"{index}. {step}")

                lines.extend([
                    "",
                    f"- Contact: {info['contact']}",
                ])

                return "\n".join(lines)

    # --------------------------------------------------------
    # Default response
    # --------------------------------------------------------

    return (
        "### Welcome to the Municipal Waste Management Assistant 🌿\n\n"
        "I can help you with:\n\n"
        "- Collection schedules for Zone A, B, C, D, or E.\n"
        "- Sorting and disposal guidelines.\n"
        "- Drop-off facility locations and hours.\n"
        "- Bulky item pickups and extra-bin requests.\n\n"
        "Try asking something like:\n"
        "• What is the pickup schedule for Zone A?\n"
        "• How do I dispose of batteries?\n"
        "• Where is the recycling center?\n"
        "• How can I book a bulk pickup?"
    )


# ============================================================
# BUILT-IN WEB PAGE
# ============================================================

INDEX_HTML = r'''<!DOCTYPE html>
<html lang="en">

<head>
<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>Municipal Waste Management Assistant</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family:
        Inter,
        Arial,
        Helvetica,
        sans-serif;

    background:
        linear-gradient(
            135deg,
            #ecfdf5 0%,
            #f8fafc 50%,
            #eff6ff 100%
        );

    color: #1f2937;
}


/* =========================================================
   MAIN APP
========================================================= */

.app {
    width: 100%;
    max-width: 1050px;

    margin: 0 auto;

    min-height: 100vh;

    padding: 24px;
}


/* =========================================================
   HEADER
========================================================= */

.header {
    position: relative;

    background:
        linear-gradient(
            135deg,
            #166534,
            #15803d
        );

    color: white;

    border-radius: 22px;

    padding: 28px;

    margin-bottom: 20px;

    box-shadow:
        0 12px 35px rgba(22, 101, 52, 0.22);

    overflow: hidden;
}

.header::after {
    content: "♻️";

    position: absolute;

    right: 25px;
    bottom: -15px;

    font-size: 90px;

    opacity: 0.12;

    transform: rotate(-12deg);
}

.header h1 {
    margin: 0 0 8px;

    font-size: 28px;

    font-weight: 800;

    letter-spacing: -0.5px;
}

.header p {
    margin: 0;

    max-width: 700px;

    color: #dcfce7;

    line-height: 1.6;
}


/* =========================================================
   QUICK ACTIONS
========================================================= */

.examples {
    display: flex;

    flex-wrap: wrap;

    gap: 9px;

    margin-top: 20px;
}

.example {
    border: 1px solid rgba(255,255,255,0.25);

    background: rgba(255,255,255,0.12);

    color: white;

    padding: 9px 13px;

    border-radius: 999px;

    cursor: pointer;

    font-size: 13px;

    transition:
        transform 0.2s ease,
        background 0.2s ease;
}

.example:hover {
    background: rgba(255,255,255,0.22);

    transform: translateY(-2px);
}


/* =========================================================
   CHAT
========================================================= */

.chat {
    background: white;

    border-radius: 22px;

    box-shadow:
        0 10px 35px rgba(15, 23, 42, 0.10);

    overflow: hidden;
}


/* =========================================================
   CHAT TOP BAR
========================================================= */

.chat-topbar {
    display: flex;

    align-items: center;

    justify-content: space-between;

    padding: 14px 18px;

    border-bottom: 1px solid #e5e7eb;

    background: #ffffff;
}

.chat-status {
    display: flex;

    align-items: center;

    gap: 9px;

    font-size: 13px;

    color: #64748b;

    font-weight: 600;
}

.status-dot {
    width: 9px;
    height: 9px;

    border-radius: 50%;

    background: #22c55e;

    box-shadow:
        0 0 0 4px #dcfce7;
}

.clear-button {
    border: 1px solid #e5e7eb;

    background: #f8fafc;

    color: #64748b;

    border-radius: 8px;

    padding: 7px 11px;

    cursor: pointer;

    font-size: 12px;
}

.clear-button:hover {
    background: #f1f5f9;
}


/* =========================================================
   MESSAGES
========================================================= */

#messages {
    height: 520px;

    overflow-y: auto;

    padding: 22px;

    scroll-behavior: smooth;
}

#messages::-webkit-scrollbar {
    width: 7px;
}

#messages::-webkit-scrollbar-thumb {
    background: #cbd5e1;

    border-radius: 10px;
}


/* Message row */

.message-row {
    display: flex;

    align-items: flex-start;

    gap: 9px;

    margin-bottom: 16px;

    animation:
        messageIn 0.25s ease;
}

.user-row {
    justify-content: flex-end;
}

@keyframes messageIn {
    from {
        opacity: 0;

        transform:
            translateY(7px);
    }

    to {
        opacity: 1;

        transform:
            translateY(0);
    }
}


/* Bot avatar */

.message-avatar {
    flex-shrink: 0;

    width: 34px;
    height: 34px;

    display: flex;

    align-items: center;

    justify-content: center;

    border-radius: 11px;

    background: #dcfce7;

    border: 1px solid #bbf7d0;

    font-size: 17px;
}


/* Base message */

.message {
    max-width: 82%;

    border-radius: 16px;

    line-height: 1.6;

    word-wrap: break-word;
}


/* Bot */

.bot {
    padding: 16px 18px;

    color: #26352b;

    background:
        linear-gradient(
            135deg,
            #f0fdf4,
            #f8fafc
        );

    border:
        1px solid #dcfce7;

    box-shadow:
        0 3px 12px rgba(15, 23, 42, 0.04);

    font-size: 14px;
}


/* User */

.user {
    padding: 12px 16px;

    color: #1e3a8a;

    background:
        linear-gradient(
            135deg,
            #dbeafe,
            #eff6ff
        );

    border:
        1px solid #bfdbfe;

    font-size: 14px;

    font-weight: 500;

    box-shadow:
        0 3px 10px rgba(37, 99, 235, 0.06);
}


/* =========================================================
   RESPONSE FORMATTING
========================================================= */

.response-title {
    display: flex;

    align-items: center;

    gap: 9px;

    margin-bottom: 15px;

    padding-bottom: 11px;

    border-bottom:
        1px solid #dcfce7;

    color: #14532d;

    font-size: 17px;

    font-weight: 800;
}

.response-title::before {
    content: "♻️";

    width: 31px;
    height: 31px;

    display: inline-flex;

    align-items: center;

    justify-content: center;

    flex-shrink: 0;

    border-radius: 9px;

    background: #dcfce7;

    font-size: 15px;
}


/* Bullet */

.response-item {
    margin: 8px 0;

    padding: 9px 12px;

    border-radius: 10px;

    background: #f8fafc;

    border-left:
        3px solid #22c55e;

    line-height: 1.55;
}


/* Numbered step */

.response-step {
    display: flex;

    align-items: flex-start;

    gap: 10px;

    margin: 9px 0;

    padding: 10px 12px;

    background: #f8fafc;

    border:
        1px solid #e2e8f0;

    border-radius: 10px;

    line-height: 1.5;
}

.step-number {
    flex-shrink: 0;

    width: 26px;
    height: 26px;

    display: flex;

    align-items: center;

    justify-content: center;

    border-radius: 50%;

    background: #16a34a;

    color: white;

    font-size: 12px;

    font-weight: 800;
}


/* Labels */

.response-label {
    display: inline-block;

    color: #166534;

    font-weight: 800;

    margin-right: 5px;
}


/* Bold */

.bot strong {
    color: #14532d;

    font-weight: 800;
}


/* =========================================================
   BIN BADGES
========================================================= */

.bin-badge {
    display: inline-block;

    padding: 4px 9px;

    margin:
        2px 3px;

    border-radius: 999px;

    font-size: 11px;

    font-weight: 800;

    vertical-align: middle;
}

.green-bin {
    background: #dcfce7;
    color: #166534;
}

.blue-bin {
    background: #dbeafe;
    color: #1d4ed8;
}

.black-bin {
    background: #e5e7eb;
    color: #111827;
}

.ewaste-bin {
    background: #f3e8ff;
    color: #7e22ce;
}

.hazardous-bin {
    background: #ffedd5;
    color: #c2410c;
}

.medical-bin {
    background: #fee2e2;
    color: #b91c1c;
}

.bulk-bin {
    background: #fef3c7;
    color: #92400e;
}


/* =========================================================
   TYPING INDICATOR
========================================================= */

.typing-row {
    display: flex;

    align-items: center;

    gap: 9px;

    margin-bottom: 15px;
}

.typing-avatar {
    width: 34px;
    height: 34px;

    display: flex;

    align-items: center;

    justify-content: center;

    border-radius: 11px;

    background: #dcfce7;

    font-size: 16px;
}

.typing {
    display: flex;

    align-items: center;

    gap: 4px;

    padding: 12px 15px;

    border-radius: 14px;

    background: #f1f5f9;
}

.typing span {
    width: 7px;
    height: 7px;

    border-radius: 50%;

    background: #64748b;

    animation:
        typingBounce 1.2s infinite;
}

.typing span:nth-child(2) {
    animation-delay: 0.15s;
}

.typing span:nth-child(3) {
    animation-delay: 0.3s;
}

@keyframes typingBounce {
    0%, 60%, 100% {
        transform: translateY(0);
        opacity: 0.5;
    }

    30% {
        transform: translateY(-4px);
        opacity: 1;
    }
}


/* =========================================================
   INPUT
========================================================= */

.input-area {
    display: flex;

    gap: 10px;

    padding: 16px;

    border-top:
        1px solid #e5e7eb;

    background: #ffffff;
}

#input {
    flex: 1;

    min-width: 0;

    padding:
        13px 15px;

    border:
        1px solid #d1d5db;

    border-radius: 11px;

    font-size: 15px;

    outline: none;

    transition:
        border-color 0.2s,
        box-shadow 0.2s;
}

#input:focus {
    border-color: #22c55e;

    box-shadow:
        0 0 0 3px #dcfce7;
}


/* Send */

#send {
    border: 0;

    border-radius: 11px;

    padding:
        0 22px;

    font-size: 15px;

    font-weight: 700;

    cursor: pointer;

    background:
        linear-gradient(
            135deg,
            #16a34a,
            #15803d
        );

    color: white;

    transition:
        transform 0.2s,
        opacity 0.2s;
}

#send:hover:not(:disabled) {
    transform: translateY(-1px);
}

#send:disabled {
    opacity: 0.6;

    cursor: not-allowed;
}


/* =========================================================
   FOOTER
========================================================= */

.footer-note {
    text-align: center;

    color: #94a3b8;

    font-size: 11px;

    padding: 12px;
}


/* =========================================================
   MOBILE
========================================================= */

@media (max-width: 600px) {

    .app {
        padding: 10px;
    }

    .header {
        padding: 22px 18px;

        border-radius: 18px;
    }

    .header h1 {
        font-size: 22px;

        padding-right: 35px;
    }

    .header p {
        font-size: 13px;
    }

    .examples {
        gap: 7px;
    }

    .example {
        font-size: 11px;

        padding: 8px 10px;
    }

    .chat {
        border-radius: 18px;
    }

    #messages {
        height: 60vh;

        padding: 15px;
    }

    .message {
        max-width: 91%;
    }

    .bot {
        padding: 14px;

        font-size: 13px;
    }

    .user {
        padding: 11px 13px;

        font-size: 13px;
    }

    .response-title {
        font-size: 15px;
    }

    .response-item {
        padding: 8px 10px;
    }

    .response-step {
        padding: 8px 10px;
    }

    .input-area {
        padding: 10px;
    }

    #input {
        font-size: 14px;
    }

    #send {
        padding: 0 15px;
    }

    .chat-topbar {
        padding: 11px 13px;
    }
}

</style>
</head>


<body>

<div class="app">

    <!-- =====================================================
         HEADER
    ====================================================== -->

    <div class="header">

        <h1>
            🌿 Municipal Waste Management Assistant
        </h1>

        <p>
            Your smart guide for waste collection schedules,
            recycling, disposal, facilities, and municipal
            waste services.
        </p>

        <div class="examples">

            <button
                class="example"
                onclick="askExample('What is the pickup schedule for Zone A?')">
                📅 Zone A Schedule
            </button>

            <button
                class="example"
                onclick="askExample('How do I dispose of batteries?')">
                🔋 Battery Disposal
            </button>

            <button
                class="example"
                onclick="askExample('Where is the recycling center?')">
                ♻️ Recycling Center
            </button>

            <button
                class="example"
                onclick="askExample('How can I book a bulk pickup?')">
                🚛 Bulk Pickup
            </button>

        </div>

    </div>


    <!-- =====================================================
         CHAT
    ====================================================== -->

    <div class="chat">

        <div class="chat-topbar">

            <div class="chat-status">
                <span class="status-dot"></span>

                <span>
                    Assistant Online
                </span>
            </div>

            <button
                class="clear-button"
                onclick="clearChat()">
                🧹 Clear Chat
            </button>

        </div>


        <div id="messages">

            <div class="message-row">

                <div class="message-avatar">
                    🌿
                </div>

                <div class="message bot">

                    <div class="response-title">
                        Welcome
                    </div>

                    <div>
                        Hello! I am your Municipal Waste
                        Management Assistant.
                    </div>

                    <br>

                    <div class="response-item">
                        • Collection schedules for Zone A, B, C,
                        D, or E.
                    </div>

                    <div class="response-item">
                        • Sorting and disposal guidelines.
                    </div>

                    <div class="response-item">
                        • Drop-off facility locations and hours.
                    </div>

                    <div class="response-item">
                        • Bulky item pickups and extra-bin requests.
                    </div>

                </div>

            </div>

        </div>


        <!-- INPUT -->

        <div class="input-area">

            <input
                id="input"
                type="text"
                placeholder="Ask your waste-management question..."
                autocomplete="off"
            >

            <button
                id="send"
                onclick="sendMessage()">
                Send
            </button>

        </div>

        <div class="footer-note">
            Municipal Waste Management Assistant
        </div>

    </div>

</div>


<script>

/* =========================================================
   ELEMENTS
========================================================= */

const input =
    document.getElementById("input");

const sendButton =
    document.getElementById("send");

const messages =
    document.getElementById("messages");


/* =========================================================
   ENTER KEY
========================================================= */

input.addEventListener(
    "keydown",
    function(event) {

        if (event.key === "Enter") {
            sendMessage();
        }

    }
);


/* =========================================================
   ADD MESSAGE
========================================================= */

function addMessage(text, type) {

    const row =
        document.createElement("div");

    row.className =
        "message-row " +
        (type === "user"
            ? "user-row"
            : ""
        );


    /* Bot avatar */

    if (type !== "user") {

        const avatar =
            document.createElement("div");

        avatar.className =
            "message-avatar";

        avatar.textContent =
            "🌿";

        row.appendChild(avatar);
    }


    /* Message */

    const div =
        document.createElement("div");

    div.className =
        "message " + type;


    if (type === "bot") {

        div.innerHTML =
            formatBotResponse(text);

    } else {

        div.textContent =
            text;
    }


    row.appendChild(div);

    messages.appendChild(row);

    messages.scrollTop =
        messages.scrollHeight;
}


/* =========================================================
   FORMAT BOT RESPONSE
========================================================= */

function formatBotResponse(text) {

    let html =
        escapeHtml(text);


    /* Markdown headings */

    html = html.replace(
        /^### (.+)$/gm,

        '<div class="response-title">$1</div>'
    );


    /* Bold */

    html = html.replace(
        /\*\*(.*?)\*\*/g,

        "<strong>$1</strong>"
    );


    /* Bullet points */

    html = html.replace(
        /^- (.+)$/gm,

        '<div class="response-item">• $1</div>'
    );


    /* Numbered steps */

    html = html.replace(
        /^\s*(\d+)\.\s+(.+)$/gm,

        '<div class="response-step">' +
        '<span class="step-number">$1</span>' +
        '<span>$2</span>' +
        '</div>'
    );


    /* Labels */

    const labels = [

        "Designated Bin / Container:",
        "Acceptable Items:",
        "Unacceptable Items:",
        "Preparation:",
        "Disposal Method:",
        "Address:",
        "Weekday Hours:",
        "Weekend Hours:",
        "Accepted Items:",
        "Fees / Incentives:",
        "Fee Structure:",
        "Description:",
        "Lead Time:",
        "Contact:",
        "Instructions:",
        "Collection Day:",
        "Time Window:"
    ];


    labels.forEach(function(label) {

        const escaped =
            label.replace(
                /[.*+?^${}()|[\]\\]/g,
                "\\$&"
            );

        html = html.replace(

            new RegExp(
                escaped,
                "g"
            ),

            '<span class="response-label">' +
            label +
            '</span>'
        );

    });


    /* =====================================================
       BIN BADGES
    ===================================================== */

    html = html.replace(
        /\b(Green)\b/g,

        '<span class="bin-badge green-bin">$1 Bin</span>'
    );

    html = html.replace(
        /\b(Blue)\b/g,

        '<span class="bin-badge blue-bin">$1 Bin</span>'
    );

    html = html.replace(
        /\b(Black)\b/g,

        '<span class="bin-badge black-bin">$1 Bin</span>'
    );


    html = html.replace(
        /\b(Special E-Waste Container)\b/g,

        '<span class="bin-badge ewaste-bin">$1</span>'
    );


    html = html.replace(
        /\b(Hazardous Waste Container)\b/g,

        '<span class="bin-badge hazardous-bin">$1</span>'
    );


    html = html.replace(
        /\b(Medical Waste Container)\b/g,

        '<span class="bin-badge medical-bin">$1</span>'
    );


    html = html.replace(
        /\b(Bulk Pickup)\b/g,

        '<span class="bin-badge bulk-bin">$1</span>'
    );


    /* Preserve line breaks */

    html =
        html.replace(
            /\n/g,
            "<br>"
        );


    return html;
}


/* =========================================================
   HTML ESCAPING
========================================================= */

function escapeHtml(text) {

    const div =
        document.createElement("div");

    div.textContent =
        text;

    return div.innerHTML;
}


/* =========================================================
   TYPING INDICATOR
========================================================= */

function showTyping() {

    const row =
        document.createElement("div");

    row.id =
        "typingIndicator";

    row.className =
        "typing-row";


    row.innerHTML = `
        <div class="typing-avatar">
            🌿
        </div>

        <div class="typing">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;


    messages.appendChild(row);

    messages.scrollTop =
        messages.scrollHeight;
}


function hideTyping() {

    const typing =
        document.getElementById(
            "typingIndicator"
        );

    if (typing) {
        typing.remove();
    }
}


/* =========================================================
   EXAMPLE QUESTIONS
========================================================= */

function askExample(text) {

    input.value =
        text;

    sendMessage();
}


/* =========================================================
   CLEAR CHAT
========================================================= */

function clearChat() {

    messages.innerHTML = `
        <div class="message-row">

            <div class="message-avatar">
                🌿
            </div>

            <div class="message bot">

                <div class="response-title">
                    Chat Cleared
                </div>

                <div>
                    Hello! How can I help you
                    with waste management today?
                </div>

            </div>

        </div>
    `;

    input.focus();
}


/* =========================================================
   SEND MESSAGE
========================================================= */

async function sendMessage() {

    const message =
        input.value.trim();


    if (
        !message ||
        sendButton.disabled
    ) {
        return;
    }


    /* User message */

    addMessage(
        message,
        "user"
    );


    input.value = "";

    sendButton.disabled =
        true;


    /* Show typing */

    showTyping();


    try {

        const response =
            await fetch(
                "/api/chat",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        message: message
                    })
                }
            );


        if (!response.ok) {

            throw new Error(
                "Server returned HTTP " +
                response.status
            );
        }


        const data =
            await response.json();


        hideTyping();


        addMessage(
            data.reply ||
            "No response received.",
            "bot"
        );


    } catch (error) {

        hideTyping();


        addMessage(
            "Could not connect to the server. " +
            "Make sure waste_app.py is still running in VS Code.",
            "bot"
        );


        console.error(error);

    } finally {

        sendButton.disabled =
            false;

        input.focus();
    }
}


/* =========================================================
   INITIAL FOCUS
========================================================= */

input.focus();

</script>

</body>
</html>
'''


# ============================================================
# HTTP SERVER
# ============================================================

class CustomHandler(SimpleHTTPRequestHandler):

    def do_GET(self):

        parsed = urlparse(self.path)

        # ----------------------------------------------------
        # Main application
        # ----------------------------------------------------

        if parsed.path in ("/", "/index.html"):

            page = INDEX_HTML.encode("utf-8")

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "text/html; charset=utf-8"
            )

            self.send_header(
                "Content-Length",
                str(len(page))
            )

            self.end_headers()

            self.wfile.write(page)

            return


        # ----------------------------------------------------
        # API data
        # ----------------------------------------------------

        if parsed.path == "/api/data":

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "application/json; charset=utf-8"
            )

            self.send_header(
                "Access-Control-Allow-Origin",
                "*"
            )

            self.end_headers()


            data = {
                "schedules": PICKUP_SCHEDULE,
                "categories": WASTE_CATEGORIES,
                "facilities": FACILITIES,
                "services": SERVICE_REQUESTS,
            }


            self.wfile.write(
                json.dumps(data).encode("utf-8")
            )

            return


        # ----------------------------------------------------
        # Do not expose Python source
        # ----------------------------------------------------

        if parsed.path == "/waste_app.py":

            self.send_error(
                404,
                "Not Found"
            )

            return


        self.send_error(
            404,
            "Not Found"
        )


    # ========================================================
    # POST
    # ========================================================

    def do_POST(self):

        parsed = urlparse(self.path)


        if parsed.path == "/api/chat":

            content_length = int(
                self.headers.get(
                    "Content-Length",
                    0
                )
            )


            body =self.rfile.read(content_length)


            try:

                payload = json.loads(
                    body.decode("utf-8")
                )


                user_msg =payload.get("message","")


                if not isinstance(
                    user_msg,
                    str
                ):

                    user_msg =str(user_msg)


                reply =process_user_chat(user_msg)


                response_data = {
                    "reply": reply,
                    "status": "success",
                }


            except Exception as error:

                response_data = {
                    "reply":
                        f"Error: {error}",

                    "status":
                        "error",
                }


            self.send_response(200)


            self.send_header(
                "Content-Type",
                "application/json"
            )


            self.send_header(
                "Access-Control-Allow-Origin",
                "*"
            )


            self.end_headers()


            self.wfile.write(
                json.dumps(
                    response_data
                ).encode("utf-8")
            )

            return


        self.send_error(
            404,
            "Endpoint Not Found"
        )


# ============================================================
# RUN SERVER
# ============================================================

def run_server():

    server_address = (
        "",
        PORT
    )


    httpd = HTTPServer(
        server_address,
        CustomHandler
    )


    print(
        f"Server starting on "
        f"http://localhost:{PORT}/"
    )

    print(
        "Open this address in Chrome or Edge "
        "to use the app."
    )

    print(
        "Press Ctrl+C to stop the server."
    )


    try:

        httpd.serve_forever()


    except KeyboardInterrupt:

        print(
            "\nServer stopped."
        )


    finally:

        httpd.server_close()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    run_server()