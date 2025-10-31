import axios from "axios";
import { useState, useEffect } from "react";

const Prediction = ({ id, setLoading, type }) => {
    const [outputs, setOutputs] = useState(null);
    
    useEffect(() => {
        if (!id || !type) return;

        let intervalId;
        setLoading(true);
        
        const getEndPoint = () => {
            if (type === "vision") return `http://localhost:8000/visionOutputs/${id}`;
            if (type === "llm") return `http://localhost:8000/llmOutputs/${id}`;
            if (type === "both") return `http://localhost:8000/llmOutputs/${id}`;
            return null;
        };

        const fetchPrediction = async () => {
            
            const endpoint = getEndPoint();
            if (!endpoint) return;

            await axios.get(endpoint)
            
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
                console.error("예측 실패 : ", err);
                setLoading(false);
                clearInterval(intervalId);
            })
        };
        fetchPrediction();
        intervalId = setInterval(fetchPrediction, 5000);

        return () => clearInterval(intervalId);
    }, [id, type]);
    
    if (!outputs) return null;

    return (    
        <div className="relative flex justify-center items-center mt-20 rounded-[28px] shadow-preview w-[550px] h-[550px]">
            {type === "vision" ? (
                outputs.map((base64Img, idx) => (
                    <img
                        key={idx}
                        src={`data:image/png;base64,${base64Img}`}
                        alt={`Prediction ${idx}`}
                        className="max-w-[500px] max-h-[500px] rounded-lg border"
                    />
                ))
            ) : (
                <div className="p-5 text-left whitespace-pre-wrap">
                    {outputs.map((text, idx) => (
                        <p key={idx}>{text}</p>
                    ))}
                </div>
            )}
        </div>
    );
};

export default Prediction;