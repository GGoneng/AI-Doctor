import { useRef } from "react";

function Chat() {
    const textareaRef = useRef(null);
    const wrapperRef = useRef(null);

    const handleScroll = () => {
        const textarea = textareaRef.current;
        const wrapper = wrapperRef.current;
        if (textarea && wrapper) {
            textarea.style.height = "auto";

            const scroll = textarea.scrollHeight;
            const maxHeight = 300;

            if (scroll > maxHeight) {
                textarea.style.height = maxHeight + "px";
                textarea.style.overflowY = "scroll";
            } else {
                textarea.style.height = scroll + "px";
                textarea.style.overflowY = "hidden";
            }

            wrapper.style.height = parseInt(textarea.style.height) + 12 + "px";
        }
    };

    return (
        <div ref={wrapperRef} className="flex fixed items-center rounded-[28px] h-auto w-[600px] bottom-[0px] mb-[30px] shadow-chat left-1/2 -translate-x-1/2">
            <textarea ref={textareaRef} onInput={handleScroll} className="h-[40px] w-[90%] border-none outline-none text-[15px] box-border pt-2 pl-1 mt-[1.7%] ml-5 bg-transparent leading-none overflow-hidden resize-none"
                                             placeholder="궁금하신 증상을 말씀해주세요"></textarea>
        </div>
    )
}

export default Chat;