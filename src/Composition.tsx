import { AbsoluteFill } from "remotion";
import { Header } from "./compositions/header";

import { z } from "zod";
import { zColor } from "@remotion/zod-types";

export const myCompSchema = z.object({
	titleText: z.string(),
	titleColor: zColor(),
});

export const MyComposition: React.FC<z.infer<typeof myCompSchema>> = ({
	titleText: propOne,
	titleColor: propTwo,
}) => {
	return (
		<AbsoluteFill className="bg-gray-100 items-center justify-center">
			<Header titleText={propOne} titleColor={propTwo} />
		</AbsoluteFill>
	);
};
