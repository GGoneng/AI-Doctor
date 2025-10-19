import Spinner from "../Data/spinner.gif";

const Loading = () => {
    
    return (
        <div className="w-full h-full">
            <img src={Spinner} className="w-20 h-20 mt-20" />
        </div>
    )
}

export default Loading;