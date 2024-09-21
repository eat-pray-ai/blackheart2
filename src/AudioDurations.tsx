import { create } from "zustand";

interface AudioDurations {
	durations: {
		[key: string]: number;
	};
	insert: (key: string, duration: number) => void;
}

const useAudioDurationsStore = create<AudioDurations>((set) => ({
	durations: {},
	insert: (key, duration) =>
		set((state) => ({
			durations: {
				...state.durations,
				[key]: duration,
			},
		})),
}));

export default useAudioDurationsStore;
