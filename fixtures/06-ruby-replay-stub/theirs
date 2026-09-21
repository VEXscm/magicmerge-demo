replay = Object.new
replay.define_singleton_method(:commit_for) { |change:, moving_tip:| moving_tip }
replay.define_singleton_method(:flush!) { true }
replay.define_singleton_method(:reader) { FakeJjStore.new }
