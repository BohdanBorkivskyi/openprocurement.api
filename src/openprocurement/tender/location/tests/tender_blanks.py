from copy import deepcopy


def create_tender(self):
    data = deepcopy(self.initial_data)
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual((response.status, response.content_type), ("201 Created", "application/json"))
