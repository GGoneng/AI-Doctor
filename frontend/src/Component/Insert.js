import { useRef } from "react";
import axios from "axios";

function Insert({ setFile }) {
    const clickRef = useRef(null);

    const currentClick = () => {
        clickRef.current.click();
    };

    const handleFile = (file) => {
        if (file && file.type.startsWith("image/")) {
            setFile(file);
            // uploadBackend(file);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        
        const File = e.dataTransfer.files[0];
        if (File && File.type.startsWith("image/")) {
            setFile(File);
            // uploadBackend(File);
        }
    };

    const handleDragOver = (e) => {
        e.preventDefault();
    };

    const handleFileselect = (e) => {
        handleFile(e.target.files[0]);
    };

    // const uploadBackend = async (file) => {
    //     const form = new FormData();
    //     form.append("file", file);

    //     await axios.post("http://localhost:8000/upload", form, {
    //         headers: {"Content-Type": "multipart/form-data"}
    //     })
    //     .then(response => console.log("서버 응답 : ", response.data))
    //     .catch(err => console.error("업로드 실패 : ", err))
    // };



    return (
        <div className="group flex items-center justify-center rounded-2xl bg-indigo-100/20 h-[350px] w-[848px] mt-20 hover:bg-indigo-100/30"
                onDrop={handleDrop} onDragOver={handleDragOver}>
            <div className="flex flex-col items-center justify-center h-[90%] w-[95%] border-2 border-transparent rounded-2xl group-hover:border-dotted group-hover:rounded-2xl group-hover:border-gray-400 p-4">
                <h1 className="font-[550] text-4xl">사진을 드래그해주세요</h1>
                <div className="mt-10 w-[100%]"></div>
                <input className="hidden" ref={clickRef} aria-hidden="true" tabIndex="-1" type="file" accept=".jpg,.jpeg,.png,.heic,.heif,.webp,.svg" 
                    onChange={handleFileselect}></input>
                <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700" onClick={currentClick} type="button">
                    <span aria-hidden="true" className="w-5 h-5">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-5 h-5">
                            <path d="M5.734 8.438C6.008 5.64 8.387 3.5 11.208 3.5a5.5 5.5 0 0 1 5.422 4.562.24.24 0 0 0 .202.19c3.026.232 5.418 2.795 5.418 5.866 0 3.25-2.642 5.882-5.896 5.882H14.75a.75.75 0 0 1 0-1.5h1.604a4.389 4.389 0 0 0 4.396-4.382c0-2.287-1.788-4.199-4.033-4.371a1.738 1.738 0 0 1-1.565-1.433A4 4 0 0 0 11.208 5C9.151 5 7.425 6.563 7.227 8.584a1.69 1.69 0 0 1-1.096 1.42 4.384 4.384 0 0 0-2.881 4.114A4.389 4.389 0 0 0 7.646 18.5h.104A4.25 4.25 0 0 0 12 14.25v-.95L9.99 15.32a.75.75 0 1 1-1.063-1.059l3.276-3.29a.75.75 0 0 1 1.063 0l3.276 3.29a.75.75 0 1 1-1.063 1.059L13.5 13.33v.919A5.75 5.75 0 0 1 7.75 20h-.104c-3.254 0-5.896-2.631-5.896-5.882a5.884 5.884 0 0 1 3.865-5.523.191.191 0 0 0 .12-.157Z" fill="currentColor"/>
                        </svg>
                    </span>
                    <span className="font-semibold">이미지 업로드하기</span>
                </button>
            </div>
        </div>
    )
};

export default Insert;