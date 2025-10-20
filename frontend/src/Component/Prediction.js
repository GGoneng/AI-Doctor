import axios from "axios";
import { useState, useEffect } from "react";

const Prediction = ({ id, setLoading }) => {
    const [outputs, setOutputs] = useState(null);
    
    useEffect(() => {
        if (!id) return;

        let intervalId;
        setLoading(true);

        const visionPredict = async () => {
            
            await axios.get(`http://localhost:8000/visionOutputs/${id}`)
            
            .then(response => {
                console.log("prediction 서버 응답 : ", response);
                const output = response.data.outputs;

                if (output && Array.isArray(output) && output.length > 0) {
                    setOutputs(output);
                    setLoading(false);
                    clearInterval(intervalId);
                }
            })
            .catch(err => {
                console.error("Vision 예측 실패 : ", err);
                setLoading(false);
                clearInterval(intervalId);
            })
        };
        visionPredict();
        intervalId = setInterval(visionPredict, 5000);

        return () => clearInterval(intervalId);
    }, [id]);
    
    if (!outputs) return null;

    return (    
        <div className="relative flex justify-center items-center mt-20 rounded-[28px] shadow-preview w-[550px] h-[550px]">
            {outputs.map((base64Img, idx) => (
                <img
                    key={idx}
                    src={`data:image/png;base64,${base64Img}`}
                    alt={`Prediction ${idx}`}
                    className="max-w-[500px] max-h-[500px] rounded-lg border"
                />
            ))}
        </div>
    )
};

export default Prediction;