import {
	spring,
	useCurrentFrame,
	useVideoConfig,
	Audio,
	staticFile,
} from "remotion";
import React from "react";
import Md5 from "crypto-js/md5";

export const Header: React.FC<{
	titleText: string;
	titleColor: string;
}> = ({ titleText, titleColor }) => {
	const audio = staticFile(`${Md5(titleText).toString()}.mp3`);
	const frame = useCurrentFrame();
	const { fps } = useVideoConfig();
	const scale = spring({
		frame: frame - 10,
		fps,
		config: {
			mass: 2,
			damping: 10,
		},
	});

	return (
		<div className="flex-1 self-start my-5 mx-9">
			<div
				style={{
					color: titleColor,
					transform: `scale(${scale})`,
					transition: "transform 0.1s ease-in-out",
				}}
				className="text-7xl"
			>
				{titleText}
			</div>
			<Audio src={audio} startFrom={0} />
		</div>
	);
};
