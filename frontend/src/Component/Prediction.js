import axios from "axios";

const Prediction = ({ id }) => {
    const visionPredict = async (id) => {
        await axios.get(`http://localhost:8000/visionOutputs/${id}`)
        .then(response => {
            const output = response.data;
            console.log("서버 응답 : ", output);
        })
        .catch(err => console.error("Vision 예측 실패 : ", err))
    };
    
    return ()
};

export default Prediction;