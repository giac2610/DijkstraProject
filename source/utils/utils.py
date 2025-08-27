import sys

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
    
    import sys

    def get_deep_size(self, obj, seen=None):
        
        size = sys.getsizeof(obj)
        if seen is None:
            seen = set()
        obj_id = id(obj)
        if obj_id in seen:
            return 0
        
        seen.add(obj_id)
        if isinstance(obj, dict):
            size += sum([self.get_deep_size(v, seen) for v in obj.values()])
            size += sum([self.get_deep_size(k, seen) for k in obj.keys()])
        elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
            size += sum([self.get_deep_size(i, seen) for i in obj])
        return size
