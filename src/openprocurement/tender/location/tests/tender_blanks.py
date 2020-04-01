from copy import deepcopy


def create_tender(self):
    data = deepcopy(self.initial_data)
    # Create tender
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual((response.status, response.content_type), ("201 Created", "application/json"))
    self.assertEqual(response.json["data"]["location"], self.initial_data["location"])

    tender_id = response.json["data"]["id"]
    acc_token = response.json["access"]["token"]

    # Try to change location(success)
    first_patch = {
        "location": {
            "latitude": "1234.5678",
            "longitude": "3456.7890"
        }
    }
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, acc_token),
        {"data": first_patch}
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertNotEqual(response.json["data"]["location"], self.initial_data["location"])
    self.assertEqual(response.json["data"]["location"], first_patch["location"])
    self.assertEqual(response.json["data"]["status"], "active.tendering")

    # Change tender status
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(tender_id), {"data": {"id": tender_id}})
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["status"], "active.auction")
    self.app.authorization = ("Basic", ("broker", ""))

    # Try to change location(not successful)
    second_patch = {
        "location": {
            "latitude": "8765.4321",
            "longitude": "0987.6543"
        }
    }
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, acc_token),
        {"data": second_patch}
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertNotEqual(response.json["data"]["location"], second_patch["location"])
    self.assertEqual(response.json["data"]["location"], first_patch["location"])
