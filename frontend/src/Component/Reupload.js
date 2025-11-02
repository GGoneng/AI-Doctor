const Reupload = ({ setID }) => {
    
    return (
        <div className="mt-5 mb-5 flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700">
            <button onClick={() => setID(null)}>다시 업로드하기</button>
        </div>
    )
}

export default Reupload;