import csv
def check_warranty(warranty_number):
    with open("app/data/warranty.csv", "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["warranty_number"] == warranty_number:
                return row

    return {"status": "not_found"}
