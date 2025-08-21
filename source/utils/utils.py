class RawData:
    def __init__(self):
        pass

    def save_to_csv(self, filename, data):
        import csv
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = data[0].keys() if data else []
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
        print(f"Data saved to {filename}")
