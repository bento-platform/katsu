from locust import HttpUser, task


class DonorWithClinicalData(HttpUser):
    @task
    def get_data(self):
        # self.client.get("/v2/authorized/api/ninja_donors")
        headers = {"Authorization": "Bearer token_2"}
        self.client.get("/v2/authorized/donor_with_clinical_data/", headers=headers)
