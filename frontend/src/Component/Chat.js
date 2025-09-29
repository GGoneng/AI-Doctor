function Chat() {
    return (
        <div className="flex fixed rounded-[28px] h-[50px] w-[600px] bottom-[0px] mb-[30px] shadow-chat left-1/2 -translate-x-1/2">
            <textarea name="prompt-textarea" className="h-[40px] w-[90%] border-none outline-none text-[15px] box-border pt-2 pl-1 mt-[1.7%] ml-5 bg-transparent leading-none overflow-hidden resize-none"
                                             placeholder="궁금하신 증상을 말씀해주세요"></textarea>
        </div>
    )
}

export default Chat;