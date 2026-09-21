pub struct ProjectionControl {
    cancelled: bool,
}

impl ProjectionControl {
    pub fn check(&self) -> Result<(), ()> {
        if self.cancelled { Err(()) } else { Ok(()) }
    }
}
