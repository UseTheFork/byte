/** @type {import('prettier').Config} */
module.exports = {
	semi: true,
	singleQuote: true,
	singleAttributePerLine: false,
	overrides: [
		{
			files: '*.jsonc',
			options: {
				trailingComma: 'none',
			},
		},
	],
};
