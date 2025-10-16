import axios from "axios";

const Prediction = ({ id }) => {
    const visionPredict = async (id) => {
        await axios.post("http://localhost:8000/predictVision", id)
        .then(response => {
            console.log("서버 응답 : ", response.data);
        })
        .catch(err => console.error("Vision 예측 실패 : ", err))
    };
    
};

export default Prediction;