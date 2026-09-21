pub struct ProjectionControl {
    cancelled: bool,
    storage: Option<String>,
}

impl ProjectionControl {
    pub fn with_storage(mut self, storage: String) -> Self {
        self.storage = Some(storage);
        self
    }

    pub fn check(&self) -> Result<(), ()> {
        if self.cancelled { Err(()) } else { Ok(()) }
    }
}
