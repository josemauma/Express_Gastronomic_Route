
def pretty_best_day(best_day):
    if not best_day:
        return "No best day found."
    date = best_day.get("best_date", "-")
    temp = best_day.get("best_temperature_avg", 0)
    wind = best_day.get("best_wind_speed", 0)
    rain = best_day.get("best_rain_probability", 0)
    line = f"**{date}**: **Avg. Temperature**: {temp:.2f} ºC, **Wind**: {wind:.2f} m/s, **Rain Prob.**: {rain}%"
    return line


def convert_dateinput_to_str(date_obj):
    """Streamlit date_input devuelve datetime.date, lo convertimos al formato DD/MM/YYYY"""
    if hasattr(date_obj, 'strftime'):
        return date_obj.strftime("%d/%m/%Y")
    return str(date_obj)

def pretty_forecast_lines(temperature_range):
    """
    Returns a list of nicely formatted strings for each forecasted day.
    """
    if not temperature_range or not isinstance(temperature_range, list):
        return ["No forecast data available."]
    lines = []
    for day in temperature_range:
        date = day.get("date")
        temp = day.get("temperature_avg")
        wind = day.get("wind_speed")
        rain = day.get("rain_probability", 0)
        line = f"**{date}**: **Avg. Temperature**: {temp:.2f} ºC, **Wind**: {wind:.2f} m/s, **Rain Prob.**: {rain}%"
        lines.append(line)
    return lines
