import axios from "axios";
import { useState, useEffect } from "react";

const Prediction = ({ id, setLoading }) => {
    const [outputs, setOutputs] = useState({ vision: [], llm: [] });
    
    useEffect(() => {
        if (!id) return;

        let intervalId;
        setLoading(true);

        const fetchPrediction = async () => {
            try {
                const [visionRes, llmRes] = await Promise.all([
                    axios.get(`http://localhost:8000/visionOutputs/${id}`),
                    axios.get(`http://localhost:8000/llmOutputs/${id}`)
                ]);

                const visionOut = visionRes.data.outputs || [];
                const llmOut = llmRes.data.outputs || [];

                if (visionOut.length === 0 && llmOut.length === 0) return;

                setOutputs({ vision: visionOut, llm: llmOut });
                setLoading(false);
                clearInterval(intervalId);
            } catch (err) {
                console.error("예측 실패 : ", err);
                setLoading(false);
                clearInterval(intervalId);
            }
        };


        fetchPrediction();
        intervalId = setInterval(fetchPrediction, 5000);

        return () => clearInterval(intervalId);
    }, [id, setLoading]);
    
    if (!outputs.vision.length && !outputs.llm.length) return null;

    return (    
        <div className="relative flex flex-col justify-center items-center mt-20 rounded-[28px] shadow-preview w-[550px] min-h-[550px] p-4">
            {outputs.vision.length > 0 && (
                <div className="flex justify-center items-center mb-5">
                    {outputs.vision.map((base64Img, idx) => (
                        <img
                            key={idx}
                            src={`data:image/png;base64,${base64Img}`}
                            alt={`Vision Prediction ${idx}`}
                            className="max-w-[500px] max-h-[500px] rounded-lg border"
                        />
                    ))}
                </div>
            )}

            {outputs.llm.length > 0 && (
                <div className="p-5 text-left whitespace-pre-wrap w-full border-t border-gray-300">
                    {outputs.llm.map((text, idx) => (
                        <p key={idx}>{text}</p>
                    ))}
                </div>
            )}
        </div>
    );
};

export default Prediction;