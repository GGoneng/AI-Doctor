import logo from "../Data/logo.png";

function Banner() {
    return (
        <a href="http://localhost:3000/" className="flex justify-center">
            <span>
                <img src={logo} alt="AI-Doctor 로고" className="w-30 h-24 ml-7"></img>
            </span> 
            <div className>

            </div>
        </a>
    );
}

export default Banner;