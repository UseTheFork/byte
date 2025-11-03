@pytest.mark.asyncio
async def test_boot_config_empty_lists(test_config: ByteConfg):
	"""Test that empty boot config lists don't cause errors."""
	# Set empty boot config (default state)
	test_config.boot.read_only_files = []
	test_config.boot.editable_files = []

	# Bootstrap container and initialize app
	container = await bootstrap(test_config)
	app = Byte(container)
	await app.initialize()

	# Verify no files in context
	file_service = await container.make(FileService)
	assert len(file_service.list_files()) == 0
