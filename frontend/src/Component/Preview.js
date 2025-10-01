function Preview({ file }) {    
    <div className="mt-6">
        {file && (
            <img
            src={URL.createObjectURL(file)}
            alt="미리보기"
            className="max-w-[300px] max-h-[300px] rounded-lg border"
            />
        )}
    </div>
}

export default Preview;