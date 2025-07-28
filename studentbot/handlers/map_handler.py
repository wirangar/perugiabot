import folium
from telegram import Update
from telegram.ext import CallbackContext

def create_map():
    # Create a map centered around Perugia
    m = folium.Map(location=[43.1122, 12.3888], zoom_start=14)

    # Add markers for important locations
    locations = {
        "University of Perugia": [43.1107, 12.3908],
        "ADiSU Office": [43.1128, 12.3868],
        "Questura di Perugia": [43.109, 12.373],
        "Agenzia delle Entrate": [43.115, 12.388],
    }

    for name, coords in locations.items():
        folium.Marker(coords, popup=name).add_to(m)

    # Save the map to an HTML file
    m.save("perugia_map.html")

async def send_map(update: Update, context: CallbackContext) -> None:
    """Sends an interactive map of Perugia."""
    create_map()
    await update.message.reply_document(open("perugia_map.html", "rb"))
