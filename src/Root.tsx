import { Composition } from "remotion";
import { MyComposition, myCompSchema } from "./Composition";
import word from "./word.json";
import "./style.css";

export const RemotionRoot: React.FC = () => {
	return (
		<>
			<Composition
				id="blackheart2"
				component={MyComposition}
				durationInFrames={240}
				fps={30}
				width={1080}
				height={1920}
				schema={myCompSchema}
				defaultProps={{
					titleText: word.word,
					titleColor: "#000000",
				}}
			/>
		</>
	);
};
