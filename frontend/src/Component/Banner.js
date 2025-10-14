import logo from "../Data/logo.png";

const Banner = () => {
    return (
        <a href="http://localhost:3000/" className="flex justify-center">
            <span>
                <img src={logo} alt="AI-Doctor 로고" className="w-30 h-24 ml-7"></img>
            </span> 
            <div>

            </div>
        </a>
    );
}

export default Banner;