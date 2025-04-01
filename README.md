# DERMALYSE APP'S API

This API call is used to detect what top 3 most probable diseases a provided image is.
Its a made with Flask framework...follow SETUP STPES to locally run it on your machine.

## API Reference

#### Send image as payload

```http
  POST :5001/predict/
```

```http
  Response {'disease1': probability1,'disease2': probability2,'disease3': probability3}
```

| Parameter | Type             | Description                                             |
| :-------- | :--------------- | :------------------------------------------------------ |
| `file`    | `base64 encoded` | **Required**. an image file converted to base64 encoded |

## Run Locally

Clone the project

```bash
  git clone https://github.com/jiten0709/DermalyseAPI.git
```

Go to the project directory

```bash
  cd DermalyseAPI
```

Create a VirtualEnv

```bash
python3.10 -m venv my_venv
```

Activate VirtualEnv

```bash
source my_venv/bin/activate
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Start the server

```bash
  python3 main.py
```

## Connect with NGROK

```bash
  ngrok http http://127.0.0.1:5001
```

which database would be best to store information about doctors and patients. my fluter app is connected to this API and I want to store the data in a database. I am using flutter for the front end and flask for the backend. I am using postgresql as my database. I want to know if it is a good choice or not. If not, please suggest me a better one.

i will use postgresql as my database. my api service should be able to list the information of patients a doctor has such as patient_name, patient_id, patient_image, disease_name, disease_probability. give me steps to create a database and tables in postgresql. also give me the code to connect my flask app with postgresql database.
