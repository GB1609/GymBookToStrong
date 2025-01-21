import csv
import sys
from collections import defaultdict
from datetime import datetime

fields_mapping = {"date": "Data", "workout": "Nome dell'allenamento"}
strong_fields = ["Date", "Workout Name", "Duration", "Exercise Name", "Set Order", "Weight", "Reps",
                 "Distance", "Seconds", "Notes", "Workout Notes", "RPE"]
gymbook_fields = ["Data", "Programma", "Orario", "Esercizio", "Zona", "Gruppi muscolari (Primari)",
                  "Gruppi muscolari (Secondari)", "Set / Set di riscaldamento / Set di defaticamento",
                  "Ripetizioni / Tempo", "Peso / Distanza", "Appunti", "Saltato"]
gymbook_path = sys.argv[1]
new_strong_path = sys.argv[2]
desired_workout = sys.argv[3] if len(sys.argv) > 3 else "all"


def build_strong_date(date, hour):
    formatted_date = datetime.strptime(date, "%d/%m/%y").strftime("%Y-%m-%d")
    return f"{formatted_date} {hour}:00"


# this is necessary otherwise Hevy create different workout for each row of same workout in same day
def fix_hour_and_duration(rows):
    # Create a dictionary to store the "Orario" value for each "Data" and "Esercizio" combination
    time_dict = {}
    min_max_dict = {}

    without_header = [row for row in rows if row["Data"] != "Data"]

    print(without_header)

    # Process the rows
    for row in without_header:  # Skip header row
        orario = row["Orario"]  # "Orario" column
        orario_time = datetime.strptime(orario, "%H:%M")
        # Key for grouping by "Data" and "Esercizio"
        key = (row["Data"], row["Programma"])
        # If the key is not in the dictionary, store the "Orario" for that group
        if key not in time_dict:
            time_dict[key] = orario
            min_max_dict[key] = {"min": orario_time, "max": orario_time}
        else:
            min_max_dict[key]["min"] = min(min_max_dict[key]["min"], orario_time)
            min_max_dict[key]["max"] = max(min_max_dict[key]["max"], orario_time)

    # Update the "Orario" column based on the groupings
    for row in without_header:
        # Update the "Orario" to the stored value for that group
        key = (row["Data"], row["Programma"])
        # Calculate the duration in minutes
        min_time = min_max_dict[key]["min"]
        max_time = min_max_dict[key]["max"]
        duration = int((max_time - min_time).total_seconds() / 60)
        row["Orario"] = time_dict[key]
        row["Durata"] = str(duration) + "m"

    return rows


def specific_rows(csv_file, workout, only_with_name=False):
    if workout == "all":
        specific_program = [row for row in csv_file if row["Programma"] != "Programma"]
    else:
        specific_program = [row for row in csv_file if str(row["Programma"]) == workout]
    removed_saltati = [row for row in specific_program if str(row["Saltato"]).lower() == "no"]
    if only_with_name:
        return [row for row in removed_saltati if str(row["Programma"]).lower() != ""]
    else:
        return removed_saltati


def add_row_number(filtered_rows):
    # Group rows by the specified fields
    groups = defaultdict(list)
    for row in filtered_rows:
        group_key = (row["Data"], row["Programma"], row["Esercizio"])  # Group by date, workout and exercise
        groups[group_key].append(row)

    # Process each group
    for group_key, rows in groups.items():
        # Sort the rows within the group by a specific column
        rows.sort(key=lambda x: x["Orario"])

        # Assign row numbers within the group
        for row_number, row in enumerate(rows, start=1):
            row["row_number"] = row_number

    return [item for sublist in groups.values() for item in sublist]


def parse_time(time):
    if "secondi" in time:
        return time.replace(" secondi", "")
    if "minuti" in time:
        return int(time.replace(" minuti", "")) * 60


def parse(row):
    new_row = {"Date": build_strong_date(row["Data"], row["Orario"]), "Workout Name": row["Programma"],
               "Duration": row["Durata"], "Exercise Name": row["Esercizio"], "Set Order": row["row_number"],
               "Weight": float(row["Peso / Distanza"]
                               .replace(" kg", "").replace(",", ".")) if row["Saltato"] == "No" and "kg" in row[
                   "Peso / Distanza"] else 0,
               "Reps": int(row["Ripetizioni / Tempo"].replace(" ripetizioni", "")) if "ripetizioni" in row[
                   "Ripetizioni / Tempo"] else 0, "Distance": float(row["Peso / Distanza"]
                                                                    .replace(" km", "").replace(",", ".")) if row[
                                                                                                                  "Saltato"] == "No" and "km" in
                                                                                                              row[
                                                                                                                  "Peso / Distanza"] else 0,
               "Seconds": parse_time(row["Ripetizioni / Tempo"]) if "ripetizioni" not in row[
                   "Ripetizioni / Tempo"] else 0, "Notes": row["Appunti"], "Workout Notes": "", "RPE": ""}

    return new_row


if __name__ == '__main__':
    with open(gymbook_path, 'r') as gymbook_file, \
            open(new_strong_path, mode='w', newline='', encoding='utf-8') as outfile:
        gymbook_csv = csv.DictReader(gymbook_file, delimiter=',')
        # distinct names of workouts
        workout_names = sorted(sorted(list(set([row["Programma"] for row in gymbook_csv]))))
        print("ALL WORKOUTS IN FILE ARE:\n" + ", ".join(workout_names))
        gymbook_file.seek(0)
        filtered_rows = specific_rows(gymbook_csv, desired_workout)
        to_elaborate_workout_names = sorted(list(set(row['Programma'] for row in filtered_rows)))
        print("WORKOUTS THAT WILL BE ELABORATE ARE:\n" + ", ".join(to_elaborate_workout_names))

        with_row_number = add_row_number(filtered_rows)
        with_time_updated = fix_hour_and_duration(with_row_number)

        # prepare a writer
        writer = csv.DictWriter(outfile, fieldnames=strong_fields)
        # Write header row to the output file
        writer.writeheader()

        for row in with_time_updated:
            parsed_row = parse(row)
            # if parsed_row["Date"].startswith("2024-09-09"):
            print(parsed_row)
            writer.writerow(parsed_row)
