from flask import Flask,request,jsonify
import pickle

app = Flask(__name__)

model = pickle.load(open("model/model.pkl","rb"))
vectorizer = pickle.load(open("model/vectorizer.pkl","rb"))

@app.route("/predict",methods=["POST"])
def predict():
    try:
        data = request.json
        text = data["text"]

        vec = vectorizer.transform([text])

        result = model.predict(vec)[0]

        return jsonify({
            "category": result
        })
    except Exception as e:
        return jsonify({"error":str(e)})

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000)