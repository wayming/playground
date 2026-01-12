#include <functional>
#include <vector>
#include <iostream>
#include <memory>

namespace SerializeFramework {

	struct SerializeUtil {
		template <typename T>
		typename std::enable_if<std::is_arithmetic<T>::value, size_t>::type
		static write(std::ostream& os, const T& data) {
			os.write(reinterpret_cast<const char*>(&data), sizeof(T));
			return sizeof(T);
		}

		template <typename T>
		typename std::enable_if<std::is_arithmetic<T>::value, T>::type
		static read(std::istream& is) {
			T data;
			is.read(reinterpret_cast<char*>(&data), sizeof(T));
			return data;
		}

		template <typename T>
		typename std::enable_if<std::is_same<std::decay_t<T>, std::string>::value, size_t>::type
		static write(std::ostream& os, const T& data) {
			size_t dataLen = data.length();
			write(os, dataLen);

			os.write(data.c_str(), dataLen);
			return dataLen + sizeof(dataLen);
		}

		template <typename T>
		typename std::enable_if<std::is_same<std::decay_t<T>, std::string>::value, std::string>::type
		static read(std::istream& in) {
			size_t strLen = read<size_t>(in);
			if (strLen == 0) return "";

			T data(strLen, '\0');
			in.read(&data[0], strLen);

			return data;
		}
	};

	enum class MessageType {
		MSG_LOGIN,
		MSG_LOGOUT
	};
	class BaseMessage {
	public:
		virtual ~BaseMessage() = default;
		virtual MessageType type() const = 0;
		virtual size_t serialize(std::ostream&) const = 0;
		virtual void deserialize(std::istream&) = 0;
	};

	class LoginMessage : public BaseMessage {
	public:
		LoginMessage() = default;
		LoginMessage(const std::string usr, const std::string pass) : userName(usr), userPass(pass) {}
		MessageType type() const { return MessageType::MSG_LOGIN; }
		size_t serialize(std::ostream& os) const {
			size_t nWrite = SerializeUtil::write(os, userName);
			nWrite += SerializeUtil::write(os, userPass);
			return nWrite;
		}

		void deserialize(std::istream& is) {
			userName = SerializeUtil::read<std::string>(is);
			userPass = SerializeUtil::read<std::string>(is);
		}

		std::string User() { return userName; }
		std::string Pass() { return userPass; }
	private:
		std::string userName;
		std::string userPass;
	};

	class Serializer {
	public:
		void in(const BaseMessage& msg, std::ostream& os) {
			
			// Write Type
			SerializeUtil::write(os, static_cast<int>(msg.type()));
			
			// Reserve Position for Length
			auto lenPos = os.tellp();
			size_t msgLen = 0;
			SerializeUtil::write(os, msgLen);

			// Write Message Body
			msgLen = msg.serialize(os);

			// Fill Length
			auto endPos = os.tellp();
			os.seekp(lenPos);
			SerializeUtil::write(os, msgLen);
			os.seekp(endPos);
		}

		std::unique_ptr<BaseMessage> out(std::istream& is) {
			auto type = SerializeUtil::read<int>(is);
			auto msgLen = SerializeUtil::read<size_t>(is);
			auto startPos = is.tellg();
			auto endPos = startPos + static_cast<std::streamoff>(msgLen);

			try {
				std::unique_ptr<BaseMessage> msg;
				if (static_cast<MessageType>(type) == MessageType::MSG_LOGIN) {
					msg = std::make_unique<LoginMessage>();
					msg->deserialize(is);
				}

				auto actualEnd = is.tellg();
				if (actualEnd < endPos) {
					// Extral field for the new version of the protocol
					is.seekg(endPos);
				}
				return msg;
			}
			catch (const std::exception& e) {
				// Ignore this message
				is.seekg(endPos);
				throw;
			}

		}
	};
}
