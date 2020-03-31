from copy import deepcopy


def create_tender(self):
    data = deepcopy(self.initial_data)
    #data.update({"status": "draft", "value": {"amount": 179511.28, "currency": "UAH", "valueAddedTaxIncluded": True}})
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual((response.status, response.content_type), ("201 Created", "application/json"))
    self.assertNotIn("value", response.json["data"])
